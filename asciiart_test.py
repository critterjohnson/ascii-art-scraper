import unittest
import random
import json
from asciiart import lambda_handler, get_artworks

class TestLambdaHandler(unittest.TestCase):
    def test_random_art(self):
        """
        Test returning a random artwork.
        """
        tries = 1
        while tries > 0:
            art = lambda_handler()
            for key, val in art.items():
                print(f"{key}: {val}")
            self.assertNotEqual(art, "")
            tries -= 1
    
    def test_line_height(self):
        """
        Test returning art of a random height between 0 and 20.
        """
        line_height = random.randint(0, 20)
        print(f"LINE HEIGHT: {str(line_height)}")

        response = lambda_handler({"queryStringParameters": {"line_height": line_height}})
        for key, val in response.items():
            print(f"{key}: {val}")
        response_body = json.loads(response["body"])
        art_lines = response_body["art"].split("\n")
        self.assertGreaterEqual(len(art_lines), line_height)


class TestHelpers(unittest.TestCase):
    def test_get_artworks(self):
        """
        Test the get_artworks function.
        """
        line_height = random.randint(0, 20)
        print(f"LINE HEIGHT: {str(line_height)}")
        count = random.randint(1, 20)
        print(f"COUNT: {str(count)}")

        art = get_artworks(count, line_height)
        print(art)


if __name__ == "__main__":
    unittest.main()
