import inspect
import swagger_api_client
from swagger_api_client.api_client import ApiException


class RestHelperLibrary(object):
    """
    Rest helper library for use with RobotFramework and swagger codegen.
    
    Example usage in a .robot file:
        
        *** Settings ***
        Library  swagger_api_client
        Library  RestHelperLibrary
        
        *** Keywords ***
        Login
            [Arguments]  ${username}  ${password}
            ${body}  Create Dictionary  ident=${username}  password=${password}
            ${login}=  Invoke API  login_user  ${body}
            [Return]  ${login}
    """
    
    @staticmethod
    def find_api_class(api_method_name):
        """
        Look up the class for an api method and return the class. Raise exceptions if not found.
        :param api_method_name: Name of the api method to locate.
                                Name should match exactly (underscores, lower case, etc.).
        :return: Api class reference
        """
        try:
            # List of all the api classes
            for api_class in inspect.getmembers(getattr(swagger_api_client, 'apis'), predicate=inspect.isclass):
                # List of all the methods in an api class
                methods = inspect.getmembers(api_class[1], predicate=inspect.ismethod)
                for method in methods:
                    if method[0] == api_method_name:
                        return api_class[1]
            raise LookupError("Could not find any matches for the method: '%s'." % api_method_name)
        except AttributeError as e:
            raise AttributeError("Could not find any matches for the method: '%s'. Error: %s" % (api_method_name, e))

    @classmethod
    def invoke_api(cls, api_method, *args, **kwargs):
        """
        Makes an API call and returns the response data as JSON
        :param api_method: The API call to execute.
        :param args: The list of arguments that are dependent on the particular API call being made.
        :param kwargs: The list of keyword arguments that are dependent on the particular API call being made.
        :return: A Python JSON object with the server's response.
        """
        # Pass in this keyword with the expected http response failure status code
        # example: expected_failure=404
        expected_failure = kwargs.pop('expected_failure', False)

        # This sets it up to return http responses instead of python
        # objects so we can use jmespath json parsing
        use_http_responses = {"_preload_content": False}
        kwargs.update(use_http_responses)

        # Look up the class for the api method
        api_class = cls.find_api_class(api_method)
        try:
            # Call the api method using the class instance
            response = getattr(api_class(), api_method)(*args, **kwargs)
        except ApiException as e:
            if e.status and expected_failure:
                return e.status == expected_failure
            else:
                raise ApiException(e)
        else:
            return cls.get_response_data_as_json(response)
