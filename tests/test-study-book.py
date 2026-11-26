import sys
import unittest
from collections import Counter
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'global/skills/study-book'))
from check import ANSWER_LINK, check_answers


class AnswerChecks(unittest.TestCase):
    def setUp(self):
        self.questions = [{'n': '1.1', 'page': 3, 'folio': '1'}]
        self.answers = [{'n': '1.1', 'page': 4, 'folio': '2'}]
        self.pages = ['', '', 'Answer 1.1, page 2 →', '1.1  A question    ← page 1\nAn answer']
        self.links = Counter({(3, 'Answer 1.1, page 2 →', 4): 1, (4, '← page 1', 3): 1})

    def problems(self):
        return check_answers(self.questions, self.answers, self.pages, self.links)

    def test_valid_links_use_physical_pages(self):
        self.assertFalse(self.problems())

    def test_rejects_correct_folio_with_wrong_link_target(self):
        for correct, wrong in [((3, 'Answer 1.1, page 2 →', 4), (3, 'Answer 1.1, page 2 →', 2)),
                               ((4, '← page 1', 3), (4, '← page 1', 1))]:
            with self.subTest(wrong=wrong):
                self.links[wrong] = self.links.pop(correct)
                self.assertTrue(self.problems())
                self.links[correct] = self.links.pop(wrong)

    def test_rejects_folio_with_extra_digit(self):
        self.pages[2] = 'Answer 1.1, page 20 →'
        self.assertTrue(self.problems())

    def test_rejects_backlink_folio_with_extra_digit(self):
        self.pages[3] = '1.1  A question    ← page 10\nAn answer'
        self.assertTrue(self.problems())

    def test_accepts_backlink_wrapped_onto_next_line_in_answer_entry(self):
        self.pages[3] = (
            '1.1  A question with a very_long_inline_code_identifier\n'
            '                                                      ← page 1\n'
            '     and more prompt text.\n'
            '     An answer'
        )
        self.assertFalse(self.problems())

    def test_rejects_missing_backlink_when_next_answer_has_same_backlink(self):
        self.questions.append({'n': '1.2', 'page': 3, 'folio': '1'})
        self.answers.append({'n': '1.2', 'page': 4, 'folio': '2'})
        self.pages[2] += '\nAnswer 1.2, page 2 →'
        self.pages[3] = (
            '1.1  First question missing its backlink\n'
            '     First answer\n'
            '1.2  Second question    ← page 1\n'
            '     Second answer'
        )
        self.links[(3, 'Answer 1.2, page 2 →', 4)] = 1
        self.links[(4, '← page 1', 3)] = 2
        self.assertTrue(self.problems())

    def test_matches_answers_heading_when_question_and_answer_share_page(self):
        self.questions = [{'n': '1.1', 'page': 4, 'folio': '2'}]
        self.answers = [{'n': '1.1', 'page': 4, 'folio': '2'}]
        self.pages[3] = (
            '1.1  A question on the same page\n'
            '     Answer 1.1, page 2 →\n'
            '\n'
            'Answers\n'
            '1.1  A question on the same page\n'
            '                                   ← page 2\n'
            '     An answer'
        )
        self.links = Counter({(4, 'Answer 1.1, page 2 →', 4): 1, (4, '← page 2', 4): 1})
        self.assertFalse(self.problems())

    def test_accepts_wrapped_prompt_starting_with_next_answer_number(self):
        self.questions.append({'n': '1.2', 'page': 3, 'folio': '1'})
        self.answers.append({'n': '1.2', 'page': 4, 'folio': '2'})
        self.pages[2] += '\nAnswer 1.2, page 2 →'
        self.pages[3] = (
            '1.1  Does the flag shipped in version\n'
            '     1.2 change the default?\n'
            '                                                      ← page 1\n'
            '     First answer\n'
            '1.2  Second question    ← page 1\n'
            '     Second answer'
        )
        self.links[(3, 'Answer 1.2, page 2 →', 4)] = 1
        self.links[(4, '← page 1', 3)] = 2
        self.assertFalse(self.problems())

    def test_supports_tagged_chapter_answers(self):
        self.questions = [{'n': 'R1.1', 'page': 3, 'folio': '8'}]
        self.answers = [{'n': 'R1.1', 'page': 4, 'folio': '9'}]
        self.pages = ['', '', 'Answer R1.1, page 9 →', 'Answers\nR1.1  Review prompt    ← page 8\nVerdict']
        self.links = Counter({(3, 'Answer R1.1, page 9 →', 4): 1, (4, '← page 8', 3): 1})
        self.assertIsNotNone(ANSWER_LINK.search('Answer R1.1, page 9 →'))
        self.assertIsNotNone(ANSWER_LINK.search('Answer R1.5.1, page 9 →'))
        self.assertIsNotNone(ANSWER_LINK.search('Answer A.1, page 9 →'))
        self.assertFalse(self.problems())

    def test_requires_each_backlink_when_two_answers_share_a_page(self):
        self.questions.append({'n': '1.2', 'page': 3, 'folio': '1'})
        self.answers.append({'n': '1.2', 'page': 4, 'folio': '2'})
        self.pages[2] += '\nAnswer 1.2, page 2 →'
        self.pages[3] += '\n1.2  Another question    ← page 1\nAnother answer'
        self.links[(3, 'Answer 1.2, page 2 →', 4)] = 1
        self.assertTrue(self.problems())
        self.links[(4, '← page 1', 3)] += 1
        self.assertFalse(self.problems())


if __name__ == '__main__':
    unittest.main()
