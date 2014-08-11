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
from .queue import Queue
import logging, time

class RpcQueue(Queue):
	""" Holds a connection to an AMQP RPC method response queue, and methods to consume from it. """
	def __init__(self, host, credentials, identifier=None, exchange=None, auto_delete=True):
		"""
		Initialize AMQP connection.

		Parameters
		----------
		host: tuple
			Must contain hostname and port to use for connection
		credentials: tuple
			Must contain username and password for this connection
		identifier: string
			Identifier for this RPC Queue. This parameter determines what the incoming queue will be called, and will also
			be used as prefix for generated correlation_ids.
			If left as None, an identifier will be generated.
		exchange: string
			If set, this RPC queue will also be bound to the given exchange using the identifier as routing key. If not,
			we will only be implicitly bound to the default exchange
		auto_delete: boolean
			Set to True to automatically delete the created RPC queue.
		"""
		self.logger = logging.getLogger(__name__)

		self.identifier = identifier

		queue = {
			"queue": self.identifier,
			"passive": False
			"durable": False,
			"auto_delete": auto_delete
		}

		binds = None
		if exchange:
			binds = [
				{ "queue": self.identifier, "exchange": exchange, "routing_key": self.identifier }
			]

		super(RpcQueue, self).__init__(host, credentials, queue, binds, exclusive=True, prefetch_count=1)

		self.responses = {}

	def consume(self, consumer_callback, exclusive=False, recover=False):
		"""
		Initialize consuming of messages from an AMQP RPC queue. Messages will be consumed after start_consuming() is called.

		An internal callback will be used to handle incoming RPC responses. Only responses that have been registered with register_response()
		will be kept internally, all other responses will be dropped silently. Responses can be accessed by using get_response().

		The internal callback will assume that the incoming RPC responses will have a correlation_id property set in the headers.

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
		self.logger.info("Asking server to requeue all unacknowledged messages")
		self.channel.basic_recover(requeue=True)

		self.consumer_tag = self.channel.basic_consume(consumer_callback=consumer_callback, queue=self.queue_name, exclusive=exclusive)

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

	def register_response(self, identifier=None):
		"""
		Register the receiving of a RPC response. Will return the given identifier after registering, or if identifier is None, will
		generate an identifier and return it after registering. If the given identifier has already been used, an unique string will
		be appended to it.

		Parameters
		----------
		identifier: string
			Identifier under which to expect a RPC callback. If None, an identifier will be generated.

		"""
		if not identifier:
			identifier = "{0}_{1}".format(self.identifier, int(time.time()))

		uniq = 1
		uniq_identifier = identifier
		while uniq_identifier in self.responses:
			uniq_identifier = "{0}_{1}".format(identifier, uniq)
			uniq += 1

		self.responses[uniq_identifier] = None
		return uniq_identifier

	def get_response(self, identifier):
		"""
		Retrieve a registered RPC response. If the identifier was not registered, an KeyError will the raised. If not value has been
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
		identifier: string
			Identifier to retrieve the RPC response for
		"""
		if identifier not in self.responses:
			raise KeyError("Given RPC response identifier was not registered.")
		if not self.responses[identifier]:
			return None

		response = self.responses[identifier]
		del(self.responses[identifier])
		return response
