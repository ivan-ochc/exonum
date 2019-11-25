"""Tests for Exonum API."""

import unittest
import time

from exonum_client import ExonumClient

from suite import run_4_nodes, assert_processes_exited_successfully


class ApiTest(unittest.TestCase):
    """Tests for Exonum API."""

    def setUp(self):
        self.network = run_4_nodes("exonum-cryptocurrency-advanced")
        time.sleep(5)

    def test_health_check(self):
        """Tests the `healthcheck` endpoint."""

        time.sleep(15)
        for validator_id in range(self.network.validators_count()):
            host, public_port, private_port = self.network.api_address(validator_id)
            client = ExonumClient(host, public_port, private_port)
            health_info_response = client.health_info()
            self.assertEqual(health_info_response.status_code, 200)
            self.assertEqual(health_info_response.json()['connected_peers'], self.network.validators_count()-1)
            self.assertEqual(health_info_response.json()['consensus_status'], 'Active')

    def test_block_response(self):
        """Tests the `block` endpoint. Check response for block"""

        for validator_id in range(self.network.validators_count()):
            host, public_port, private_port = self.network.api_address(validator_id)
            client = ExonumClient(host, public_port, private_port)
            block_response = client.get_block(1)
            self.assertEqual(block_response.status_code, 200)
            self.assertEqual(block_response.json()['height'], 1)
            self.assertEqual(block_response.json()['tx_count'], 0)
            self.assertIsNotNone(block_response.json()['time'])

    def test_zero_block(self):
        """Tests the `block` endpoint. Check response for 0 block"""

        for validator_id in range(self.network.validators_count()):
            host, public_port, private_port = self.network.api_address(validator_id)
            client = ExonumClient(host, public_port, private_port)
            block_response = client.get_block(0)
            self.assertEqual(block_response.status_code, 200)
            self.assertEqual(block_response.json()['height'], 0)

    def test_nonexistent_block(self):
        """Tests the `block` endpoint. Check response for nonexistent block"""

        nonexistent_height = 999
        for validator_id in range(self.network.validators_count()):
            host, public_port, private_port = self.network.api_address(validator_id)
            client = ExonumClient(host, public_port, private_port)
            block_response = client.get_block(nonexistent_height)
            self.assertEqual(block_response.status_code, 404)

    def test_get_only_non_empty_blocks(self):
        """Tests the `blocks` endpoint. Check response for only non empty blocks"""

        for validator_id in range(self.network.validators_count()):
            host, public_port, private_port = self.network.api_address(validator_id)
            client = ExonumClient(host, public_port, private_port)
            blocks_response = client.get_blocks(count=5, skip_empty_blocks=True)
            self.assertEqual(blocks_response.status_code, 200)
            self.assertEqual(len(blocks_response.json()['blocks']), 0)

    def test_get_last_n_blocks(self):
        """Tests the `blocks` endpoint. Check response for last N blocks"""

        number_of_blocks = 5
        time.sleep(5)
        for validator_id in range(self.network.validators_count()):
            host, public_port, private_port = self.network.api_address(validator_id)
            client = ExonumClient(host, public_port, private_port)
            blocks_response = client.get_blocks(count=number_of_blocks)
            self.assertEqual(blocks_response.status_code, 200)
            self.assertEqual(len(blocks_response.json()['blocks']), number_of_blocks)

    def test_get_blocks_with_time(self):
        """Tests the `blocks` endpoint. Check response for blocks with time"""

        for validator_id in range(self.network.validators_count()):
            host, public_port, private_port = self.network.api_address(validator_id)
            client = ExonumClient(host, public_port, private_port)
            blocks_response = client.get_blocks(count=1, add_blocks_time=True)
            self.assertEqual(blocks_response.status_code, 200)
            self.assertIsNotNone(blocks_response.json()['blocks'][0]['time'])

    def test_get_blocks_with_precommits(self):
        """Tests the `blocks` endpoint. Check response for blocks with precommits"""
        # TODO: Add test after ECR-3875 is implemented

    def test_get_n_latest_blocks(self):
        """Tests the `blocks` endpoint. Check response for N latest blocks"""

        latest = 5
        number_of_blocks = 15
        for validator_id in range(self.network.validators_count()):
            height_counter = latest
            host, public_port, private_port = self.network.api_address(validator_id)
            client = ExonumClient(host, public_port, private_port)
            blocks_response = client.get_blocks(count=number_of_blocks, latest=latest)
            for block in blocks_response.json()['blocks']:
                self.assertEqual(int(block['height']), height_counter)
                height_counter -= 1

    def test_get_n_latest_blocks_negative(self):
        """Tests the `blocks` endpoint. Check response for N latest blocks if latest exceeds current height"""

        latest = 999
        number_of_blocks = 6
        for validator_id in range(self.network.validators_count()):
            host, public_port, private_port = self.network.api_address(validator_id)
            client = ExonumClient(host, public_port, private_port)
            blocks_response = client.get_blocks(count=number_of_blocks, latest=latest)
            self.assertEqual(blocks_response.status_code, 404)
            current_height = client.get_blocks(count=1).json()['blocks'][0]['height']
            expected_error_msg = "Requested latest height {} is greater than " \
                                 "the current blockchain height {}".format(latest, current_height)
            self.assertEqual(blocks_response.content.decode('UTF-8'), expected_error_msg)

    def test_get_n_earliest_blocks(self):
        """Tests the `blocks` endpoint. Check response for N earliest blocks"""
        # TODO: Add test after ECR-3875 is implemented

    def test_get_mix_latest_earliest_blocks(self):
        """Tests the `blocks` endpoint. Check response for N latest and earliest blocks"""
        # TODO: Add test after ECR-3875 is implemented

    def test_get_unknown_transaction(self):
        """Tests the `transactions` endpoint. Check response for unknown transaction"""

        for validator_id in range(self.network.validators_count()):
            host, public_port, private_port = self.network.api_address(validator_id)
            client = ExonumClient(host, public_port, private_port)
            tx_response = client.get_tx_info("b2d09e1bddca851bee8faf8ffdcfc18cb87fbde167a29bd049fa2eee4a82c1ca")
            self.assertEqual(tx_response.status_code, 404)
            self.assertEqual(tx_response.json()['type'], "unknown")

    def test_zero_initial_stats(self):
        """Tests the `stats` endpoint. Check initial stats values"""

        for validator_id in range(self.network.validators_count()):
            host, public_port, private_port = self.network.api_address(validator_id)
            client = ExonumClient(host, public_port, private_port)
            stats = client.stats()
            self.assertEqual(stats.status_code, 200)
            self.assertEqual(stats.json()['tx_count'], 0)
            self.assertEqual(stats.json()['tx_pool_size'], 0)
            self.assertEqual(stats.json()['tx_cache_size'], 0)

    def test_user_agent(self):
        """Tests the `user_agent` endpoint."""

        for validator_id in range(self.network.validators_count()):
            host, public_port, private_port = self.network.api_address(validator_id)
            client = ExonumClient(host, public_port, private_port)
            user_agent_response = client.user_agent()
            self.assertEqual(user_agent_response.status_code, 200)

    def tearDown(self):
        outputs = self.network.stop()
        assert_processes_exited_successfully(self, outputs)