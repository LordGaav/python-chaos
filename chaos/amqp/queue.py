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

""" AMQP consumer related classes and functions. """

import logging
import pika
from pika.exceptions import ChannelClosed

class Queue(object):
	""" Holds a connection to an AMQP queue, and methods to consume from it. """
	def __init__(self, host, credentials, queue, binds=None, prefetch_count=4):
		"""
		Initialize AMQP connection.

		Parameters
		----------
		host: tuple
			Must contain hostname and port to use for connection
		credentials: tuple
			Must contain username and password for this connection
		queue: dict
			Must contain at least the following keys:
				queue: string - what queue to use
				passive: boolean - should we use an existing queue, to try to declare our own
			Options below are optional when passive = True
				durable: boolean - should the queue be durable
				auto_delete: boolean - should we auto delete the queue when we close the connection
		binds: list of dicts
			A list of dicts with the following keys:
				queue: string - name of the queue to bind
				exchange: string - name of the exchange to bind
				routing_key: string - routing key to use for this bind
		prefetch_count: int
			Define how many items may be prefetched at a time.
			The default value of 4 is a workaround of an issue that exists in python-pika 0.9.13. See
			the Github issue for more info: https://github.com/pika/pika/issues/286 .
		"""
		self.logger = logging.getLogger(__name__)

		self.logger.info("Creating AMQP connection to {0}:{1}".format(host[0], host[1]))
		self.credentials = pika.PlainCredentials(credentials[0], credentials[1])
		self.parameters = pika.ConnectionParameters(host=host[0], port=host[1], credentials=self.credentials)
		self.connection = pika.BlockingConnection(self.parameters)
		self.channel = self.connection.channel()
		self.channel.basic_qos(prefetch_count=4)

		self.queue_name = queue['queue']
		self.logger.info("Declaring queue {0}".format(self.queue_name))
		self.channel.queue_declare(**queue)

		if binds:
			self._perform_binds(binds)

	def _perform_binds(self, binds):
		"""
		Binds queues to exchanges.

		Parameters
		----------
		binds: list of dicts
			a list of dicts with the following keys:
				queue: string - name of the queue to bind
				exchange: string - name of the exchange to bind
				routing_key: string - routing key to use for this bind
		"""
		for bind in binds:
			self.logger.debug("Binding queue {0} to exchange {1} with key {2}".format(bind['queue'], bind['exchange'], bind['routing_key']))
			self.channel.queue_bind(**bind)

	def _perform_unbinds(self, binds):
		"""
		Unbinds queues from exchanges.

		Parameters
		----------
		binds: list of dicts
			A list of dicts with the following keys:
				queue: string - name of the queue to bind
				exchange: string - name of the exchange to bind
				routing_key: string - routing key to use for this bind
		"""
		for bind in binds:
			self.logger.debug("Unbinding queue {0} from exchange {1} with key {2}".format(bind['queue'], bind['exchange'], bind['routing_key']))
			self.channel.queue_unbind(**bind)

	def close(self):
		"""
		Closes the internal connection.
		"""
		self.cancel()
		self.logger.debug("Closing AMQP connection")
		try:
			self.connection.close()
		except Exception, eee:
			self.logger.warning("Received an error while trying to close AMQP connection: " + str(eee))

	def cancel(self, consumer_tag=None):
		"""
		Cancels the current consuming action by using the stored consumer_tag. If a consumer_tag is given, that one is used instead.

		Parameters
		----------
		consumer_tag: string
			Tag of consumer to cancel
		"""
		if not consumer_tag:
			if not hasattr(self, "consumer_tag"):
				return
			consumer_tag = self.consumer_tag
		self.channel.basic_cancel(consumer_tag)

	def consume(self, consumer_callback, exclusive=False, recover=False):
		"""
		Initialize consuming of messages from an AMQP queue. Messages will be consumed after start_consuming() is called.

		Calling this method multiple times with exclusive active will result in a pika.exceptions.ChannelClosed Error.

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
		recover: boolean
			Asks the server to requeue all previously delivered but not acknowledged messages. This can be used to recover from a sudden
			disconnect or other error.

		Returns
		-------
		string
			Returns a generated consumer_tag.
		"""
		if recover:
			self.logger.info("Asking server to requeue all unacknowledged messages")
			self.channel.basic_recover(requeue=True)
		self.consumer_tag = self.channel.basic_consume(consumer_callback=consumer_callback, queue=self.queue_name, exclusive=exclusive)
		return self.consumer_tag

	def start_consuming(self):
		"""
		Start consuming messages.
		"""
		self.channel.start_consuming()

	def stop_consuming(self):
		"""
		Stop consuming messages.
		"""
		self.channel.stop_consuming()
