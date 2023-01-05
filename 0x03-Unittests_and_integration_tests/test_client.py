#!/usr/bin/env python3
import unittest
from unittest.mock import patch, PropertyMock
from parameterized import parameterized, parameterized_class

import client
from client import GithubOrgClient
from fixtures import TEST_PAYLOAD


class TestGithubOrgClient(unittest.TestCase):
    """
    Test the GithubOrgClient class methods
    """
    @parameterized.expand([
        ("google"),
        ("abc")
    ])
    @patch('client.get_json', return_value={"payload": True})
    def test_org(self, org, mock_org):
        """
        Test TestGithubOrgClient's org method
        Args:
            org (str): organisation's name
        """
        org_test = GithubOrgClient(org)
        test_response = org_test.org
        self.assertEqual(test_response, mock_org.return_value)
        mock_org.assert_called_once()

    def test_public_repos_url(self):
        """
        Test TestGithubOrgClient's _public_repos_url method works
        as expected.
        """
        with patch.object(GithubOrgClient,
                          'org',
                          new_callable=PropertyMock) as m:
            m.return_value = {"repos_url": "89"}
            test_org = GithubOrgClient('holberton')
            test_repo_url = test_org._public_repos_url
            self.assertEqual(test_repo_url, m.return_value.get('repos_url'))
            m.assert_called_once()

    @patch('client.get_json', return_value=[{'name': 'Holberton'},
                                            {'name': '89'},
                                            {'name': 'alx'}])
    def test_public_repos(self, mock_repo):
        """
        Test GithubOrgClient's public_repos method
        """
        with patch.object(GithubOrgClient,
                          '_public_repos_url',
                          new_callable=PropertyMock,
                          return_value="https://api.github.com/") as m:

            test_client = GithubOrgClient('holberton')
            test_repo = test_client.public_repos()
            for idx in range(3):
                self.assertIn(mock_repo.return_value[idx]['name'], test_repo)
            mock_repo.assert_called_once()
            m.assert_called_once()

    @parameterized.expand([
        ({"license": {"key": "my_license"}}, "my_license", True),
        ({"license": {"key": "other_license"}}, "my_license", False)
    ])
    def test_has_license(self, repo, license_key, expected):
        """
        Test GithubOrgClient's has_license method
        Args:
            repo (dict): dictionary
            license_key (str): license in the repo dict
        """
        test_instance = GithubOrgClient('holberton')
        license_available = test_instance.has_license(repo, license_key)
        self.assertEqual(license_available, expected)


def requests_get(*args, **kwargs):
    """
    Function that mocks requests.get function
    Returns the correct json data based on the given input url
    """
    class MockResponse:
        """
        Mock response
        """
        def __init__(self, json_data):
            self.json_data = json_data

        def json(self):
            return self.json_data

    if args[0] == "https://api.github.com/orgs/google":
        return MockResponse(TEST_PAYLOAD[0][0])
    if args[0] == TEST_PAYLOAD[0][0]["repos_url"]:
        return MockResponse(TEST_PAYLOAD[0][1])


@parameterized_class(
    ('org_payload', 'repos_payload', 'expected_repos', 'apache2_repos'),
    [(TEST_PAYLOAD[0][0], TEST_PAYLOAD[0][1], TEST_PAYLOAD[0][2],
      TEST_PAYLOAD[0][3])]
)
class TestIntegrationGithubOrgClient(unittest.TestCase):
    """
    Integration test for the GithubOrgClient.public_repos method
    """
    @classmethod
    def setUpClass(cls):
        """
        Set up function for TestIntegrationGithubOrgClient class
        Sets up a patcher to be used in the class methods
        """
        cls.get_patcher = patch('utils.requests.get', side_effect=requests_get)
        cls.get_patcher.start()
        cls.client = GithubOrgClient('google')

    @classmethod
    def tearDownClass(cls):
        """
        Tear down resources set up for class tests.
        Stops the patcher that had been started
        """
        cls.get_patcher.stop()

    def test_public_repos(self):
        """
        Test public_repos method without license
        """
        self.assertEqual(self.client.public_repos(), self.expected_repos)

    def test_public_repos_with_license(self):
        """
        Test public_repos method with license
        """
        self.assertEqual(
            self.client.public_repos(license="apache-2.0"),
            self.apache2_repos)
