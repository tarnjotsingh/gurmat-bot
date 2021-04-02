# coding: utf-8

"""
    Jaap Counter

    No description provided (generated by Swagger Codegen https://github.com/swagger-api/swagger-codegen)  # noqa: E501

    OpenAPI spec version: 1.0.0
    
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""

import pprint
import re  # noqa: F401

import six

class JaapDetailsSet(object):
    """NOTE: This class is auto generated by the swagger code generator program.

    Do not edit the class manually.
    """
    """
    Attributes:
      swagger_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    swagger_types = {
        'title': 'str',
        'description': 'str',
        'goal': 'float'
    }

    attribute_map = {
        'title': 'title',
        'description': 'description',
        'goal': 'goal'
    }

    def __init__(self, title=None, description=None, goal=None):  # noqa: E501
        """JaapDetailsSet - a model defined in Swagger"""  # noqa: E501
        self._title = None
        self._description = None
        self._goal = None
        self.discriminator = None
        if title is not None:
            self.title = title
        if description is not None:
            self.description = description
        if goal is not None:
            self.goal = goal

    @property
    def title(self):
        """Gets the title of this JaapDetailsSet.  # noqa: E501


        :return: The title of this JaapDetailsSet.  # noqa: E501
        :rtype: str
        """
        return self._title

    @title.setter
    def title(self, title):
        """Sets the title of this JaapDetailsSet.


        :param title: The title of this JaapDetailsSet.  # noqa: E501
        :type: str
        """

        self._title = title

    @property
    def description(self):
        """Gets the description of this JaapDetailsSet.  # noqa: E501


        :return: The description of this JaapDetailsSet.  # noqa: E501
        :rtype: str
        """
        return self._description

    @description.setter
    def description(self, description):
        """Sets the description of this JaapDetailsSet.


        :param description: The description of this JaapDetailsSet.  # noqa: E501
        :type: str
        """

        self._description = description

    @property
    def goal(self):
        """Gets the goal of this JaapDetailsSet.  # noqa: E501


        :return: The goal of this JaapDetailsSet.  # noqa: E501
        :rtype: float
        """
        return self._goal

    @goal.setter
    def goal(self, goal):
        """Sets the goal of this JaapDetailsSet.


        :param goal: The goal of this JaapDetailsSet.  # noqa: E501
        :type: float
        """

        self._goal = goal

    def to_dict(self):
        """Returns the model properties as a dict"""
        result = {}

        for attr, _ in six.iteritems(self.swagger_types):
            value = getattr(self, attr)
            if isinstance(value, list):
                result[attr] = list(map(
                    lambda x: x.to_dict() if hasattr(x, "to_dict") else x,
                    value
                ))
            elif hasattr(value, "to_dict"):
                result[attr] = value.to_dict()
            elif isinstance(value, dict):
                result[attr] = dict(map(
                    lambda item: (item[0], item[1].to_dict())
                    if hasattr(item[1], "to_dict") else item,
                    value.items()
                ))
            else:
                result[attr] = value
        if issubclass(JaapDetailsSet, dict):
            for key, value in self.items():
                result[key] = value

        return result

    def to_str(self):
        """Returns the string representation of the model"""
        return pprint.pformat(self.to_dict())

    def __repr__(self):
        """For `print` and `pprint`"""
        return self.to_str()

    def __eq__(self, other):
        """Returns true if both objects are equal"""
        if not isinstance(other, JaapDetailsSet):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
