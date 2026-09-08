import unittest
import requests
from markupsafe import escape

BASE_URL = "http://localhost:5000"

# ==============================================================================
# Helper Wrapper Functions
# ==============================================================================

def get_user_profile(identifier: int|str|None = None) -> requests.Response:
    """Helper function to call the /user/ route endpoints."""
    url: str = f'{BASE_URL}/user/'
    if isinstance(identifier, int):
        url = f"{BASE_URL}/user/{identifier}"
    elif isinstance(identifier, str):
        url = f"{BASE_URL}/user/@{identifier}"
    return requests.get(url)

def get_lotto_drawing(n: int, k: int) -> requests.Response:
    """Helper function to call the /lotto/<n>/<k> endpoint."""
    url: str = f"{BASE_URL}/lotto/{n}/{k}"
    return requests.get(url)

def get_search_results(params: dict[str,str|int] | None = None) -> requests.Response:
    """Helper function to call the /search endpoint with query parameters."""
    return requests.get(f"{BASE_URL}/search", params=params)


# ==============================================================================
# Custom Test Result Runner to Track Points
# ==============================================================================

class PointScoringTestResult(unittest.TextTestResult):
    """Custom test result collector that tracks point values for each test."""

    def __init__(self, stream, descriptions, verbosity):
        super().__init__(stream, descriptions, verbosity)
        self.earned_points = 0
        self.total_possible_points = 0
        self.failures_with_points = []

    def _get_points(self, test) -> int:
        """Safely extracts _point_value from standard tests and _SubTest instances."""
        # Handle subtests (test.test_case points back to the parent TestCase)
        actual_test = getattr(test, "test_case", test)
        method_name = getattr(actual_test, "_testMethodName", None)
        
        if method_name:
            method = getattr(actual_test, method_name, None)
            return getattr(method, "_point_value", 0)
        return getattr(actual_test, "_point_value", 0)

    def startTest(self, test):
        super().startTest(test)
        # Avoid double-counting total points for subtests inside a single test method
        if not hasattr(test, "test_case"):
            self.total_possible_points += self._get_points(test)

    def addSuccess(self, test):
        super().addSuccess(test)
        # Only add points when the parent test method completes (not per individual subtest)
        if not hasattr(test, "test_case"):
            self.earned_points += self._get_points(test)

    def addFailure(self, test, err):
        super().addFailure(test, err)
        points = self._get_points(test)
        error_message: str = self._exc_info_to_string(err, test) # type: ignore
        self.failures_with_points.append((test, points, error_message))

    def addError(self, test, err):
        super().addError(test, err)
        points = self._get_points(test)
        error_message: str = self._exc_info_to_string(err, test) # type: ignore
        self.failures_with_points.append((test, points, error_message))

class PointScoringTestRunner(unittest.TextTestRunner):
    """Custom runner that displays point breakdowns and total scores."""
    resultclass = PointScoringTestResult

    def run(self, test):
        result: PointScoringTestResult = super().run(test) # type: ignore
        print("\n" + "=" * 70)
        print("GRADED POINT BREAKDOWN SUMMARY")
        print("=" * 70)

        if result.failures_with_points:
            print("\nFAILED TEST DETAILS & POINTS DEDUCTED:")
            for test, points, err_str in result.failures_with_points:
                test_name = test.id().split(".")[-1]
                print(f"\n[-] {test_name} FAILED: Lost {points} pts")
                # Print abbreviated failure info
                first_line_err = err_str.strip().split("\n")[-1]
                print(f"    Reason: {first_line_err}")
        else:
            print("\nAll tests passed cleanly!")

        print("-" * 70)
        print(f"TOTAL SCORE: {result.earned_points} / {result.total_possible_points} pts")
        print("=" * 70 + "\n")
        return result


def points(val):
    """Decorator to attach point values to test methods."""
    def decorator(fn):
        fn._point_value = val
        return fn
    return decorator


# ==============================================================================
# Homework 2 Test Suite
# ==============================================================================

class TestHomework2(unittest.TestCase):

    # --------------------------------------------------------------------------
    # Problem 1: User Profile Tests (32 pts Total)
    # --------------------------------------------------------------------------

    @points(8)
    def test_user_profile_uid(self):
        """Tests /user/<int:uid> across multiple integer IDs (8 pts)."""
        test_uids = [42, 1, 99999, 100]
        for uid in test_uids:
            with self.subTest(uid=uid):
                response = get_user_profile(uid)
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.text, f"User ID: {uid}")

    @points(8)
    def test_user_profile_username(self):
        """Tests /user/@<string:username> across multiple string usernames (8 pts)."""
        test_usernames = ["bdickinson", "alice", "user_123", "developer-pro"]
        for username in test_usernames:
            with self.subTest(username=username):
                response = get_user_profile(username)
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.text, f"User Profile: {username}")

    @points(8)
    def test_user_profile_default_guest(self):
        """Tests /user/ without uid or username, expecting default guest (8 pts)."""
        response = get_user_profile()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.text, "User Profile: guest")

    @points(8)
    def test_user_profile_xss_escape(self):
        """Tests /user/@<username> escaping raw HTML/JS via markupsafe.escape (8 pts)."""
        xss_payloads: tuple[str,...] = (
            "<img src=x onerror=alert(1)>",
            '<input type="password" value="">',
        )
        for payload in xss_payloads:
            with self.subTest(payload=payload):
                response = get_user_profile(payload)
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.text, f"User Profile: {escape(payload)}")

    # --------------------------------------------------------------------------
    # Problem 2: Lotto Drawing Tests (32 pts Total)
    # --------------------------------------------------------------------------

    @points(4)
    def test_lotto_zero_k(self):
        """Tests /lotto/<n>/<k> with k=0, expecting a 400 status (4 pts)."""
        response = get_lotto_drawing(10, 0)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.text, "Error: cannot create an empty sample")

    @points(4)
    def test_lotto_zero_n(self):
        """Tests /lotto/<n>/<k> with n=0, expecting a 400 status (4 pts)."""
        response = get_lotto_drawing(0, 5)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.text, "Error: cannot sample from an empty range")

    @points(4)
    def test_lotto_k_greater_than_n(self):
        """Tests /lotto/<n>/<k> with k > n, expecting a 400 status (4 pts)."""
        response = get_lotto_drawing(5, 10)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.text, "Error: sample size k cannot exceed total range")

    @points(20)
    def test_lotto_valid_params(self):
        """Tests /lotto/<n>/<k> with multiple valid n & k combinations (20 pts)."""
        valid_cases = [
            (49, 6),
            (10, 10),
            (100, 1),
            (20, 5),
        ]

        for n, k in valid_cases:
            with self.subTest(n=n, k=k):
                response = get_lotto_drawing(n, k)
                self.assertEqual(response.status_code, 200)

                # Parse and validate space-delimited result string
                numbers = response.text.split(" ")
                self.assertEqual(len(numbers), k, f"Expected {k} space-delimited numbers for n={n}, k={k}")

                parsed_ints = [int(num) for num in numbers]
                self.assertEqual(len(set(parsed_ints)), k, f"Sampled numbers for n={n}, k={k} must be unique")
                self.assertTrue(
                    all(1 <= num <= n for num in parsed_ints),
                    f"All numbers for n={n}, k={k} must be within range 1 to {n}",
                )

    # --------------------------------------------------------------------------
    # Problem 3: Search Tests (36 pts Total)
    # --------------------------------------------------------------------------

    @points(4)
    def test_search_default_values(self):
        """Tests /search with no query parameters, ensuring fallback defaults (4 pts)."""
        response = get_search_results()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.text, 'Page 1 of search results for "everything"')

    @points(4)
    def test_search_invalid_page_error(self):
        """Tests /search with a non-integer page parameter, expecting a 400 status (4 pts)."""
        invalid_pages = ["abc", "1.5", "one", "true"]
        for page in invalid_pages:
            with self.subTest(page=page):
                response = get_search_results({"page": page})
                self.assertEqual(response.status_code, 400)
                self.assertEqual(response.text, "Error: page must be an integer")

    @points(20)
    def test_search_valid_query_and_page(self):
        """Tests /search with valid custom query and page arguments (16 pts)."""
        valid_searches = [
            ("python flask", 3, 'Page 3 of search results for "python flask"'),
            ("web programming", 1, 'Page 1 of search results for "web programming"'),
            ("algorithms", 42, 'Page 42 of search results for "algorithms"'),
        ]

        for query, page, expected_str in valid_searches:
            with self.subTest(query=query, page=page):
                response = get_search_results({"query": query, "page": page})
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.text, expected_str)

    @points(8)
    def test_search_xss_escape(self):
        """Tests /search query argument escaping via markupsafe.escape (8 pts)."""
        xss_queries = [
            "<b onmouseover=alert('xss')>test</b>",
            "<script>window.location='http://attacker.com'</script>",
        ]
        for raw_query in xss_queries:
            with self.subTest(query=raw_query):
                response = get_search_results({"query": raw_query, "page": 1})
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.text, f'Page 1 of search results for "{escape(raw_query)}"')


# ==============================================================================
# Script Execution Entry Point
# ==============================================================================

if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(TestHomework2)
    PointScoringTestRunner(verbosity=1).run(suite)
