# Copyright (c) 2014 Nick Douma < n.douma [at] nekoconeko . nl >
#
# This file is part of chaos, a.k.a. python-chaos .
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 3.0 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library. If not, see
# <http://www.gnu.org/licenses/>.

""" AMQP RPC type event consumer related classes and functions. """

from __future__ import absolute_import
from .exchange import publish_message
from .exceptions import MessageNotDelivered, MessageDeliveryTimeout
from .queue import Queue
import logging
import time
import uuid


class Rpc(Queue):
	"""
	Attempts to simplify RPC style calls using AMQP exchanges and queues. This works two-fold:
	* This class will create an Exchange for sending RPC messages.
	* This class will also create a Queue for handling responses to the RPC messages.
	Additionally, this class can also create a 'normal' Queue, to avoid having to create a separate instance.
	All of the above is created using a single AMQP channel.
	"""
	def __init__(self, host, credentials, identifier=None, prefetch_count=1, exchange=None, auto_delete=True, queue=None, binds=None, confirm_delivery=False):
		"""
		Initialize AMQP connection.

		Parameters
		----------
		host: tuple
			Must contain hostname and port to use for connection
		credentials: tuple
			Must contain username and password for this connection
		identifier: string
			Identifier for this RPC Queue. This parameter determines what the incoming queue will be called.
			If left as None, an identifier will be generated.
		prefetch_count: int
			Set the prefetch_count of all queues defined by this class.
		exchange: string
			If set, this RPC queue will also be bound to the given exchange using the identifier as routing key. If not,
			we will only be implicitly bound to the default exchange
		auto_delete: boolean
			Set to True to automatically delete the created RPC queue.
		queue: dict
			Create a separate queue based on the given parameters. This is a general purpose AMQP queue, and can be
			provided a separate callback using consume().
			Must contain at least the following keys:
				queue: string - what queue to use
				passive: boolean - should we use an existing queue, to try to declare our own
			Options below are optional when passive = True
				durable: boolean - should the queue be durable
				auto_delete: boolean - should we auto delete the queue when we close the connection
		binds: list of dicts
			A list of dicts  with the following keys:
				queue: string - name of the queue to bind
				exchange: string - name of the exchange to bind
				routing_key: string - routing key to use for this bind
		confirm_delivery: boolean
			If True, basic.Confirm will be set on the current channel.
		"""
		self.logger = logging.getLogger(__name__)

		self.rpc_queue_name = identifier
		if not self.rpc_queue_name:
			self.rpc_queue_name = "rpc.{0}".format(int(time.time()))

		rpc_queue = {
			"queue": self.rpc_queue_name,
			"passive": False,
			"durable": False,
			"auto_delete": auto_delete
		}
		if exchange:
			binds.append({"queue": self.rpc_queue_name, "exchange": exchange, "routing_key": self.rpc_queue_name})

		super(Rpc, self).__init__(host, credentials, rpc_queue, None)

		if queue:
			self.queue_name = queue['queue']
			self.logger.info("Declaring general purpose queue {0}".format(self.queue_name))
			self.channel.queue_declare(**queue)
		else:
			del(self.queue_name)

		if binds:
			self._perform_binds(binds)

		self.channel.basic_qos(prefetch_count=prefetch_count)

		if confirm_delivery:
			self.channel.confirm_delivery()

		self.responses = {}

	def consume(self, consumer_callback=None, exclusive=False):
		"""
		Initialize consuming of messages from an AMQP RPC queue. Messages will be consumed after start_consuming() is called.

		An internal callback will be used to handle incoming RPC responses. Only responses that have been registered with register_response()
		will be kept internally, all other responses will be dropped silently. Responses can be accessed by using get_response().

		The internal callback will assume that the incoming RPC responses will have a correlation_id property set in the headers.

		Additionally, if a general purpose queue was created on construction, the parameters to this function can be used to declare a callback
		and options for that queue. A ValueError is raised when trying to set a general purpose callback, but no queue was declared during
		construction.

		In contrast to the Queue class, the recover parameter is missing from this implementation of consume(). We will always try to requeue
		old messages.

		Parameters
		----------
		consumer_callback: callback
			Function to call when a message is consumed. The callback function will be called on each delivery,
			and will receive three parameters:
				* channel
				* method_frame
				* header_frame
				* body
		exclusive: boolean
			Is this consumer supposed to be the exclusive consumer of the given queue?
		"""
		if not hasattr(self, "queue_name") and consumer_callback:
			raise ValueError("Trying to set a callback, while no general purpose queue was declared.")

		self.rpc_consumer_tag = self.channel.basic_consume(consumer_callback=self._rpc_response_callback, queue=self.rpc_queue_name, exclusive=False)

		if consumer_callback:
			super(Rpc, self).consume(consumer_callback, exclusive, True)

	def _rpc_response_callback(self, channel, method_frame, header_frame, body):
		"""
		Internal callback used by consume()

		Parameters
		----------
		channel: object
			Channel from which the callback originated
		method_frame: dict
			Information about the message
		header_frame: dict
			Headers of the message
		body: string
			Body of the message
		"""
		self.logger.debug("Received RPC response with correlation_id: {0}".format(header_frame.correlation_id))
		if header_frame.correlation_id in self.responses:
			self.responses[header_frame.correlation_id] = {
				"method_frame": method_frame,
				"header_frame": header_frame,
				"body": body
			}
		channel.basic_ack(method_frame.delivery_tag)

	def register_response(self, correlation_id=None):
		"""
		Register the receiving of a RPC response. Will return the given correlation_id after registering, or if correlation_id is None, will
		generate a correlation_id and return it after registering. If the given correlation_id has already been used, an KeyError will be
		raised.

		UUID version 1 will be used when generating correlation_ids. Depending on the underlying system and implementation, this will guarantee
		that generated values are unique between workers. At least CPython guarantees this behaviour.

		Parameters
		----------
		correlation_id: string
			Identifier under which to expect a RPC callback. If None, a correlation_id will be generated.

		"""
		if not correlation_id:
			correlation_id = str(uuid.uuid1())

		if correlation_id in self.responses:
			raise KeyError("Correlation_id {0} was already registered, and therefor not unique.".format(correlation_id))

		self.responses[correlation_id] = None
		return correlation_id

	def retrieve_available_responses(self):
		"""
		Retrieve a list of all available responses. Will return a list of correlation_ids.
		"""
		return [k for (k, v) in self.responses.iteritems() if v]

	def retrieve_response(self, correlation_id):
		"""
		Retrieve a registered RPC response. If the correlation_id was not registered, an KeyError will the raised. If not value has been
		received yet, None will be returned. After retrieving the response, the value will be unset internally.

		The returned value will include the entire RabbitMQ message, consisting of a dict with the following keys:

			method_frame: dict
				Information about the message
			header_frame: dict
				Headers of the message
			body: string
				Body of the message

		Parameters
		----------
		correlation_id: string
			Identifier to retrieve the RPC response for
		"""
		if correlation_id not in self.responses:
			raise KeyError("Given RPC response correlation_id was not registered.")
		if not self.responses[correlation_id]:
			return None

		response = self.responses[correlation_id]
		del(self.responses[correlation_id])
		return response

	def request_response(self, exchange, routing_key, message, properties=None, correlation_id=None, timeout=6):
		"""
		This function wraps publish, and sets the properties necessary to allow end-to-end communication using the Rpc paradigm.

		This function assumes that the named exchange and routing_key combination will result in a AMQP queue to pickup the request, and
		reply using another AMQP message. To achieve this, the following properties are set, along with any custom properties:
		* correlation_id: a correlation_id is generated using register_response. It is assumed that the responding service will also provide
			the same id in the response.
		* reply_to: this is set to the internal RPC queue name, so we can pickup responses.

		The mandatory bit will be set on the message as a mechanism to detect if the message was delivered to a queue.
		This is to avoid needlessly waiting on a reply, when the message wasn't delivered in the first place.

		Parameters
		----------
		exchange: string
			Exchange to publish to.
		routing_key: string
			Routing key to use for this message.
		message: string
			Message to publish.
		properties: dict
			Properties to set on message. This parameter is optional, but if set, at least the following options must be set:
				content_type: string - what content_type to specify, default is 'text/plain'.
				delivery_mode: int - what delivery_mode to use. By default message are not persistent, but this can be
					set by specifying PERSISTENT_MESSAGE .
		correlation_id: string
			Custom correlation_id. This identifier is subject to the same semantics and logic as register_response().
		timeout: int
			How many seconds to wait for a reply. If no reply is received, an MessageDeliveryTimeout is raised. Set to
			False to wait forever.
		"""
		if not properties:
			properties = {}
		properties['correlation_id'] = self.register_response(correlation_id)
		properties['reply_to'] = self.rpc_queue_name

		if not self.publish(exchange, routing_key, message, properties, mandatory=True):
			self.retrieve_response(properties['correlation_id'])
			raise MessageNotDelivered("Message was not delivered to a queue")

		start = int(time.time())
		self.channel.force_data_events(True)
		while properties['correlation_id'] not in self.retrieve_available_responses():
			self.connection.process_data_events()
			if timeout and (int(time.time()) - start) > timeout:
				self.retrieve_response(properties['correlation_id'])
				raise MessageDeliveryTimeout("No response received from RPC server within specified period")

		return self.retrieve_response(properties['correlation_id'])

	def publish(self, exchange, routing_key, message, properties=None, mandatory=False):
		"""
		Publish a message to an AMQP exchange.

		Parameters
		----------
		exchange: string
			Exchange to publish to.
		routing_key: string
			Routing key to use for this message.
		message: string
			Message to publish.
		properties: dict
			Properties to set on message. This parameter is optional, but if set, at least the following options must be set:
				content_type: string - what content_type to specify, default is 'text/plain'.
				delivery_mode: int - what delivery_mode to use. By default message are not persistent, but this can be
					set by specifying PERSISTENT_MESSAGE .
		mandatory: boolean
			If set to True, the mandatory bit will be set on the published message.
		"""
		return publish_message(self.channel, exchange, routing_key, message, properties, mandatory)

	def reply(self, original_headers, message, properties=None):
		"""
		Reply to a RPC request. This function will use the default exchange, to directly contact the reply_to queue.

		Parameters
		----------
		original_headers: dict
			The headers of the originating message that caused this reply.
		message: string
			Message to reply with
		properties: dict
			Properties to set on message. This parameter is optional, but if set, at least the following options must be set:
				content_type: string - what content_type to specify, default is 'text/plain'.
				delivery_mode: int - what delivery_mode to use. By default message are not persistent, but this can be
					set by specifying PERSISTENT_MESSAGE .
		"""
		rpc_reply(self.channel, original_headers, message, properties)


def rpc_reply(channel, original_headers, message, properties=None):
	"""
	Reply to a RPC request. This function will use the default exchange, to directly contact the reply_to queue.

	Parameters
	----------
	channel: object
		Properly initialized AMQP channel to use.
	original_headers: dict
		The headers of the originating message that caused this reply.
	message: string
		Message to reply with
	properties: dict
		Properties to set on message. This parameter is optional, but if set, at least the following options must be set:
			content_type: string - what content_type to specify, default is 'text/plain'.
			delivery_mode: int - what delivery_mode to use. By default message are not persistent, but this can be
				set by specifying PERSISTENT_MESSAGE .
	"""
	if not properties:
		properties = {}
	properties['correlation_id'] = original_headers.correlation_id

	publish_message(channel, '', original_headers.reply_to, message, properties)
