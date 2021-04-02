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

class JaapDetailsCondition(object):
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
        'formname': 'str'
    }

    attribute_map = {
        'formname': 'formname'
    }

    def __init__(self, formname=None):  # noqa: E501
        """JaapDetailsCondition - a model defined in Swagger"""  # noqa: E501
        self._formname = None
        self.discriminator = None
        if formname is not None:
            self.formname = formname

    @property
    def formname(self):
        """Gets the formname of this JaapDetailsCondition.  # noqa: E501


        :return: The formname of this JaapDetailsCondition.  # noqa: E501
        :rtype: str
        """
        return self._formname

    @formname.setter
    def formname(self, formname):
        """Sets the formname of this JaapDetailsCondition.


        :param formname: The formname of this JaapDetailsCondition.  # noqa: E501
        :type: str
        """

        self._formname = formname

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
        if issubclass(JaapDetailsCondition, dict):
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
        if not isinstance(other, JaapDetailsCondition):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
