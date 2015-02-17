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

""" AMQP exchange related classes and functions. """

import logging
import pika

NORMAL_MESSAGE = 1
PERSISTENT_MESSAGE = 2


class Exchange(object):
	""" Holds a connection to an AMQP exchange, and methods to publish to it. """
	def __init__(self, host, credentials, exchange=None, routing_key=None):
		"""
		Initialize AMQP connection.

		Parameters
		----------
		host: tuple
			Must contain hostname and port to use for connection
		credentials: tuple
			Must contain username and password for this connection
		exchange: dict
			Must contain at least the following keys:
				exchange: string - what exchange to use
				exchange_type: string - what type of exchange to use ("direct")
				passive: boolean - should we use an existing exchange, or try to declare our own
			Options below are optional when passive = True
				durable: boolean - should the exchange be durable
				auto_delete: boolean - should we auto delete the exchange when we close the connection
		routing_key: string
			what routing_key to use for published messages. If unset, this parameter must be set during publishing
		"""
		self.logger = logging.getLogger(__name__)

		self.logger.debug("Creating connection to {0}:{1}".format(host[0], host[1]))
		self.default_routing_key = routing_key
		self.credentials = pika.PlainCredentials(credentials[0], credentials[1])
		self.parameters = pika.ConnectionParameters(host=host[0], port=host[1], credentials=self.credentials)
		self.connection = pika.BlockingConnection(self.parameters)
		self.channel = self.connection.channel()

		if exchange:
			self.exchange_name = exchange['exchange']
			self.logger.debug("Declaring exchange {0}".format(self.exchange_name))
			self.channel.exchange_declare(**exchange)
		else:
			self.exchange_name = None

	def close(self):
		"""
		Closes the internal connection.
		"""
		self.logger.debug("Closing AMQP connection")
		self.connection.close()

	def publish(self, message, properties=None, mandatory=False):
		"""
		Publish a message to an AMQP exchange.

		Parameters
		----------
		message: string
			Message to publish.
		properties: dict
			Properties to set on message. This parameter is optional, but if set, at least the following options must be set:
				content_type: string - what content_type to specify, default is 'text/plain'.
				delivery_mode: int - what delivery_mode to use. By default message are not persistent, but this can be
					set by specifying PERSISTENT_MESSAGE .
			The following options are also available:
				routing_key: string - what routing_key to use. MUST be set if this was not set during __init__.
				exchange: string - what exchange to use. MUST be set if this was not set during __init__.
		mandatory: boolean
			If set to True, the mandatory bit will be set on the published message.

		Returns
		-------
		Depending on the mode of the Channel, the return value can signify different things:

		basic_Confirm is active:
			True means that the message has been delivered to a queue, False means it hasn't.
		mandatory bit was set on message:
			True means that the message has been delivered to a consumer, False means that it has been returned.
		No special bit or mode has been set:
			None is returned.
		"""
		return publish_message(self.channel, self.exchange_name, self.default_routing_key, message, properties, mandatory)


def publish_message(channel, exchange, routing_key, message, properties=None, mandatory=False):
	"""
	Publish a message to an AMQP exchange.

	Parameters
	----------
	channel: object
		Properly initialized AMQP channel to use.
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
		The following options are also available:
			routing_key: string - what routing_key to use. Will override the one set in the parameters.
			exchange: string - what exchange to use. Will override the one set in the parameters.
	mandatory: boolean
		If set to True, the mandatory bit will be set on the published message.

	Returns
	-------
	Depending on the mode of the Channel, the return value can signify different things:

	basic_Confirm is active:
		True means that the message has been delivered to a queue, False means it hasn't.
	mandatory bit was set on message:
		True means that the message has been delivered to a consumer, False means that it has been returned.
	No special bit or mode has been set:
		None is returned.
	"""
	if properties is None:
		properties = {}
	if properties and "routing_key" in properties:
		routing_key = properties["routing_key"]
		del(properties["routing_key"])
	if properties and "exchange" in properties:
		exchange = properties["exchange"]
		del(properties["exchange"])

	if not routing_key:
		raise ValueError("routing_key was not specified")
	if not exchange and not exchange == "":
		raise ValueError("exchange was not specified")

	logging.getLogger(__name__ + ".publish_message").debug("Publishing message to exchange {0} with routing_key {1}".format(exchange, routing_key))

	return channel.basic_publish(exchange, routing_key, message, pika.BasicProperties(**properties), mandatory)
