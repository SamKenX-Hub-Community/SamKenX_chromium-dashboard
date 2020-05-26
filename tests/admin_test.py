# Copyright 2020 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License")
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import unittest
import testing_config  # Must be imported before the module under test.
import urllib

import mock
import webapp2
from webob import exc

import models
import admin


class FeatureHandlerTest(unittest.TestCase):

  def setUp(self):
    self.feature_1 = models.Feature(
        name='feature one', summary='sum', category=1, visibility=1,
        standardization=1, web_dev_views=1, impl_status_chrome=1)
    self.feature_1.put()

    request = webapp2.Request.blank(
        '/admin/features/edit/%d' % self.feature_1.key().id())
    response = webapp2.Response()
    self.handler = admin.FeatureHandler(request, response)

  def test_post__anon(self):
    """Anon cannot edit features, gets a 401."""
    testing_config.sign_out()
    feature_id = self.feature_1.key().id()
    actual = self.handler.post(self.handler.request.path, feature_id=feature_id)
    self.assertIsNone(actual)
    self.assertEqual('401 Unauthorized', self.handler.response.status)

  @mock.patch('admin.FeatureHandler.redirect')
  def test_post__no_existing(self, mock_redirect):
    """Trying to edit a feature that does not exist redirects."""
    testing_config.sign_in('user1@google.com', 123567890)
    mock_redirect.return_value = 'fake redirect return value'
    bad_feature_id = self.feature_1.key().id() + 1
    path = '/admin/features/edit/%d' % bad_feature_id
    self.handler.request = webapp2.Request.blank(path)
    actual = self.handler.post(path, feature_id=bad_feature_id)
    self.assertEqual('fake redirect return value', actual)
    mock_redirect.assert_called_once()

  @mock.patch('admin.FeatureHandler.redirect')
  def test_post__normal(self, mock_redirect):
    """Allowed user can edit a feature."""
    testing_config.sign_in('user1@google.com', 123567890)
    mock_redirect.return_value = 'fake redirect return value'
    feature_id = self.feature_1.key().id()
    params = {
      "category": 1,
      "name": "name",
      "summary": "sum",
      "impl_status_chrome": 1,
      "footprint": 1,
      "visibility": 1,
      "ff_views": 1,
      "ie_views": 1,
      "safari_views": 1,
      "web_dev_views": 1,
      "standardization": 1,
      "experiment_goals": "Measure something",
      }
    path = '/admin/features/edit/%d' % feature_id
    self.handler.request = webapp2.Request.blank(
        path, POST=urllib.urlencode(params))
    actual = self.handler.post(path, feature_id=feature_id)
    self.assertEqual('fake redirect return value', actual)
    mock_redirect.assert_called_once_with('/feature/%d' % feature_id)
    updated_feature = models.Feature.get_by_id(feature_id)
    self.assertEqual('Measure something', updated_feature.experiment_goals)