import unittest

from vesna.alh import CRCError
from vesna.alh import signalgenerator

#import logging
#logging.basicConfig(level=logging.DEBUG)

class TestSignalGenerator(unittest.TestCase):

	def test_get_config_list(self):

		class TestALH:
			def get(self, resource):
				return "dev #0, Test, 1 configs:\n" \
					"  cfg #0: Test:\n" \
					"     base: 10 Hz, spacing: 1 Hz, bw: 1 Hz, channels: 10, min power: -10 dBm, max power: 0 dBm, time: 1 ms"

		alh = TestALH()
		s = signalgenerator.SignalGenerator(alh)

		cl = s.get_config_list()

		self.assertEqual(len(cl.devices), 1)
		self.assertEqual(len(cl.configs), 1)

	def test_get_config_list_corrupt_1(self):

		class TestALH:
			def get(self, resource):
				return ""

		alh = TestALH()
		s = signalgenerator.SignalGenerator(alh)

		cl = s.get_config_list()

		self.assertEqual(cl.configs, [])
		self.assertEqual(cl.devices, [])

	def test_get_config_list_corrupt_2(self):

		class TestALH:
			def get(self, resource):
				return "dev #0, Test, 2 configs:"

		alh = TestALH()
		s = signalgenerator.SignalGenerator(alh)

		self.assertRaises(CRCError, s.get_config_list)

	def test_get_config_list_corrupt_3(self):

		class TestALH:
			def get(self, resource):
				return "dev #0, Test, 1 configs:\n"\
					"  cfg #0: Test:"

		alh = TestALH()
		s = signalgenerator.SignalGenerator(alh)

		self.assertRaises(CRCError, s.get_config_list)


class TestGeneratorConfigList(unittest.TestCase):
	def test_get_config_name(self):
		cl = signalgenerator.ConfigList()

		d = signalgenerator.Device(0, "test")
		cl._add_device(d)

		def add_dc(id, name, base):
			dc = signalgenerator.DeviceConfig(id, name, d)
			dc.base = base 
			dc.spacing = 1
			dc.num = 1000
			dc.time = 1
			dc.min_power = -100
			dc.max_power = 0
			cl._add_config(dc)

		add_dc(0, "foo 1", 1000)
		add_dc(1, "foo 2", 2000)
		add_dc(2, "bar 1", 1000)
		add_dc(3, "bar 2", 2000)

		sc = cl.get_tx_config(1500, 0)
		self.assertEqual(0, sc.config.id)

		sc = cl.get_tx_config(2500, 0)
		self.assertEqual(1, sc.config.id)

		sc = cl.get_tx_config(1500, 0, name="bar")
		self.assertEqual(2, sc.config.id)

		sc = cl.get_tx_config(2500, 0, name="bar")
		self.assertEqual(3, sc.config.id)

from vesna.alh.spectrumsensor import SpectrumSensor, SpectrumSensorResult, SpectrumSensorProgram
from vesna.spectrumsensor import Device, DeviceConfig, SweepConfig, Sweep

class TestSpectrumSensor(unittest.TestCase):

	def test_get_config_list(self):

		class TestALH:
			def get(self, resource):
				s =	"dev #0, Test, 1 configs:\n" \
					"  cfg #0: Test:\n" \
					"     base: 10 Hz, spacing: 1 Hz, bw: 1 Hz, channels: 10, time: 1 ms"
				return s.encode('ascii')

		alh = TestALH()
		s = SpectrumSensor(alh)

		cl = s.get_config_list()

		self.assertEqual(len(cl.devices), 1)
		self.assertEqual(len(cl.configs), 1)

	def test_get_config_list_corrupt_1(self):

		class TestALH:
			def get(self, resource):
				return "".encode('ascii')

		alh = TestALH()
		s = SpectrumSensor(alh)

		cl = s.get_config_list()

		self.assertEqual(cl.configs, [])
		self.assertEqual(cl.devices, [])

	def test_get_config_list_corrupt_2(self):

		class TestALH:
			def get(self, resource):
				s = "dev #0, Test, 2 configs:"
				return s.encode('ascii')

		alh = TestALH()
		s = SpectrumSensor(alh)

		self.assertRaises(CRCError, s.get_config_list)

	def test_get_config_list_corrupt_3(self):

		class TestALH:
			def get(self, resource):
				s = "dev #0, Test, 1 configs:\n"\
					"  cfg #0: Test:"
				return s.encode('ascii')

		alh = TestALH()
		s = SpectrumSensor(alh)

		self.assertRaises(CRCError, s.get_config_list)

class TestSpectrumSensorResult(unittest.TestCase):
	def setUp(self):
		d = Device(0, "test")

		dc = DeviceConfig(0, "foo", d)
		dc.base = 1000
		dc.spacing = 1
		dc.num = 1000

		sc = SweepConfig(dc, 0, 3, 1)

		p = SpectrumSensorProgram(sc, 0, 10, 1)

		self.r = r = SpectrumSensorResult(p)

		s = Sweep()
		s.timestamp = 0.0
		s.data = [ 0.0, 1.0, 2.0 ]
		r.sweeps.append(s)

		s = Sweep()
		s.timestamp = 1.0
		s.data = [ 3.0, 4.0 ]
		r.sweeps.append(s)

	def test_get_data(self):
		self.assertEqual( [
			[ 0.0, 1.0, 2.0 ],
			[ 3.0, 4.0, 4.0 ]
		], self.r.get_data())

	def test_get_hz_list(self):
		self.assertEqual( [ 1000.0, 1001.0, 1002.0 ], self.r.get_hz_list() )

	def test_get_s_list(self):
		self.assertEqual( [ 0.0, 1.0 ], self.r.get_s_list() )

from vesna.alh import ALHProtocol

class TestALHProtocol(unittest.TestCase):
	def test_is_printable_1(self):
		self.assertEqual(ALHProtocol._is_printable("foo".encode('ascii')), True)

	def test_is_printable_2(self):
		self.assertEqual(ALHProtocol._is_printable("\x00".encode('ascii')), False)

	def test_is_printable_3(self):
		self.assertEqual(ALHProtocol._is_printable(u"\x8f".encode('latin2')), False)

try:
	from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
except ImportError:
	from http.server import HTTPServer, BaseHTTPRequestHandler

import threading
from vesna.alh import ALHWeb

class TestALHWeb(unittest.TestCase):
	def setUp(self):

		self.last_headers = last_headers = [None]
		self.srv_response = srv_response = [None]

		class MockHTTPRequestHandler(BaseHTTPRequestHandler):
			def do_GET(self):
				last_headers[0] = self.headers

				self.send_response(200)
				self.end_headers()

				self.wfile.write(srv_response[0])

			def log_message(self, format, *args):
				pass

		server_address = ('localhost', 12345)
		self.httpd = HTTPServer(server_address, MockHTTPRequestHandler)
		self.t = threading.Thread(target=self.httpd.serve_forever)
		self.t.start()

	def tearDown(self):
		self.httpd.shutdown()
		self.t.join()
		self.httpd.server_close()

	def test_get_ascii(self):
		self.srv_response[0] = 'bar'.encode('ascii')

		alh = ALHWeb("http://localhost:12345", "id")
		r = alh.get("foo")

		self.assertEqual(r, self.srv_response[0])
		self.assertIn('alh', self.last_headers[0]['User-Agent'])

	def test_get_bin(self):
		self.srv_response[0] = '\x00\x01\x02\x04'.encode('ascii')

		alh = ALHWeb("http://localhost:12345", "id")
		r = alh.get("foo")

		self.assertEqual(r, self.srv_response[0])
