from requests import get
from json import loads
from io import StringIO
from pandas import json_normalize, read_csv
from cryptography.fernet import Fernet
from tempfile import NamedTemporaryFile
from pynssp.core.container import NSSPContainer, APIGraph
from pynssp.core.constants import HTTP_STATUSES


class Token:
    """A Token Class Representing a Token object

    A Token object has a token string and a key.
    A Token object can get API data via an API URL.

    :param token: a token string
    :param access_token: type of HTTP authentication. 
        Should be "Bearer" or "Basic". (Default value = "Bearer")
    :ivar access_token: HTTP authentication type.

    :examples:
        >>> from pynssp import Token
        >>> 
        >>> myTokenProfile = Token("abc123")
    """


    def __init__(self, token, access_token="Bearer"):
        """Initializes a new Token object.
        """
        self.__k = Fernet(Fernet.generate_key())
        self.__token = NSSPContainer(self.__k.encrypt(token.encode()))
        self.access_token = access_token


    def get_api_response(self, url):
        """Get API response

        :param url: a string of API URL
        :returns: an object of class response
        """
        headers = {
            "Authorization": "{} {}".
            format(self.access_token, self.__k.decrypt(self.__token.value).decode())
        }
        response = get(url, headers = headers)
        print("{}: {}".format(response.status_code, HTTP_STATUSES[str(response.status_code)]))
        if response.status_code == 200:
            return response


    def get_api_data(self, url, fromCSV=False, encoding="utf-8", **kwargs):
        """Get API data

        :param url: a string of API URL
        :param fromCSV: a logical, defines whether data are received in .csv format or .json format (Default value = False)
        :param encoding: an encoding standard (Default value = "utf-8")
        :param **kwargs: Additional keyword arguments to pass to `pandas.read_csv()` if `fromCSV` is True.
        :returns: A pandas dataframe
        """
        response_content = self.get_api_response(url).content
        if not fromCSV:
            return loads(response_content)
        else:
            return read_csv(StringIO(response_content.decode(encoding)))


    def get_api_graph(self, url, file_ext=".png"):
        """Get API graph

        :param url: a string of API URL
        :param file_ext: a non-empty character vector giving the file extension. (Default value = ".png")
        :returns: an object of type APIGraph
        """
        response = self.get_api_response(url)
        img_file = NamedTemporaryFile(suffix=file_ext, delete=False)
        img_file.write(response.content)
        return APIGraph(path=img_file.name, response=response)


    def pickle(self, file=None, file_ext=".pkl"):
        """Save an object of class Credentials to file

        :param file_ext: a non-empty character vector giving the file extension. (Default value = ".pkl")
        :param file:  (Default value = None)
        """
        from pickle import dump
        file_name = "tokenProfile" + file_ext
        if file is not None:
            file_name = file
        with open(file_name, "wb") as f:
            dump(self, f)
