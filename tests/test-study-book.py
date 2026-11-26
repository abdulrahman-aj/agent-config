import sys
import unittest
from collections import Counter
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'global/skills/study-book'))
from check import ANSWER_LINK, check_answers, parse_answer_links


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
        self.assertIsNotNone(ANSWER_LINK.search('Answer É.1, page 9 →'))
        self.assertFalse(self.problems())

    def test_accepts_wrapped_prompt_starting_with_later_answer_numbers(self):
        self.questions = [
            {'n': 'R1.1', 'page': 2, 'folio': '7'},
            {'n': 'R1.2', 'page': 3, 'folio': '8'},
            {'n': 'R1.3', 'page': 3, 'folio': '8'},
        ]
        self.answers = [
            {'n': 'R1.1', 'page': 4, 'folio': '9'},
            {'n': 'R1.2', 'page': 4, 'folio': '9'},
            {'n': 'R1.3', 'page': 4, 'folio': '9'},
        ]
        self.pages = [
            '',
            'Answer R1.1, page 9 →',
            'Answer R1.2, page 9 →\nAnswer R1.3, page 9 →',
            (
                'Answers\n'
                'R1.1  Compare the behavior of\n'
                '      R1.2 and\n'
                '      R1.3 with a very_long_inline_code_identifier\n'
                '                                                    ← page 7\n'
                '      First answer.\n'
                'R1.2  Second prompt                                 ← page 8\n'
                '      Second answer.\n'
                'R1.3  Third prompt                                  ← page 8\n'
                '      Third answer.'
            ),
        ]
        self.links = Counter({
            (2, 'Answer R1.1, page 9 →', 4): 1,
            (3, 'Answer R1.2, page 9 →', 4): 1,
            (3, 'Answer R1.3, page 9 →', 4): 1,
            (4, '← page 7', 2): 1,
            (4, '← page 8', 3): 2,
        })
        self.assertFalse(self.problems())

    def test_rejects_swapped_backlinks_masked_by_plain_text_in_answer_body(self):
        questions = [
            {'n': 'R1.1', 'page': 2, 'folio': '7'},
            {'n': 'R1.2', 'page': 3, 'folio': '8'},
        ]
        answers = [
            {'n': 'R1.1', 'page': 4, 'folio': '9'},
            {'n': 'R1.2', 'page': 4, 'folio': '9'},
        ]
        pages = [
            '',
            'Answer R1.1, page 9 →',
            'Answer R1.2, page 9 →',
            (
                'Answers\n'
                'R1.1  First prompt                                  ← page 8\n'
                '      See ← page 7 in the text.\n'
                'R1.2  Second prompt                                 ← page 7\n'
                '      See ← page 8 in the text.'
            ),
        ]
        xml = """<pdf2xml>
          <page number="2">
            <text top="100" left="94" height="16"><a href="book.html#4">Answer R1.1, page 9 →</a></text>
          </page>
          <page number="3">
            <text top="100" left="94" height="16"><a href="book.html#4">Answer R1.2, page 9 →</a></text>
          </page>
          <page number="4">
            <text top="21" left="562" height="16">Answers</text>
            <text top="81" left="55" height="25"><b>Answers</b></text>
            <text top="113" left="55" height="18"><b>R1.1</b></text>
            <text top="114" left="584" height="15"><a href="book.html#3"><b>← page 8</b></a></text>
            <text top="200" left="55" height="18"><b>R1.2</b></text>
            <text top="201" left="584" height="15"><a href="book.html#2"><b>← page 7</b></a></text>
          </page>
        </pdf2xml>"""
        links, row_backlinks = parse_answer_links(xml, 'book.html', answers)
        problems = check_answers(questions, answers, pages, links, row_backlinks)
        self.assertEqual(len(problems), 2)
        self.assertTrue(any('R1.1' in p for p in problems))
        self.assertTrue(any('R1.2' in p for p in problems))

        # Swap back so R1.1 links to #2 (← page 7) and R1.2 links to #3 (← page 8).
        fixed_xml = """<pdf2xml>
          <page number="2">
            <text top="100" left="94" height="16"><a href="book.html#4">Answer R1.1, page 9 →</a></text>
          </page>
          <page number="3">
            <text top="100" left="94" height="16"><a href="book.html#4">Answer R1.2, page 9 →</a></text>
          </page>
          <page number="4">
            <text top="21" left="562" height="16">Answers</text>
            <text top="81" left="55" height="25"><b>Answers</b></text>
            <text top="113" left="55" height="18"><b>R1.1</b></text>
            <text top="114" left="584" height="15"><a href="book.html#2"><b>← page 7</b></a></text>
            <text top="200" left="55" height="18"><b>R1.2</b></text>
            <text top="201" left="584" height="15"><a href="book.html#3"><b>← page 8</b></a></text>
          </page>
        </pdf2xml>"""
        links_ok, row_backlinks_ok = parse_answer_links(fixed_xml, 'book.html', answers)
        self.assertFalse(check_answers(questions, answers, pages, links_ok, row_backlinks_ok))

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
