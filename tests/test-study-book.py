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
        self.pages = ['', '', 'Answer 1.1, page 2 →', '']
        self.links = Counter({(3, 'Answer 1.1, page 2 →', 4): 1})
        self.row_backlinks = {(4, '1.1'): ('← page 1', 3)}

    def problems(self):
        return check_answers(
            self.questions, self.answers, self.pages, self.links, self.row_backlinks
        )

    def test_valid_links_use_physical_pages(self):
        self.assertFalse(self.problems())

    def test_rejects_correct_folio_with_wrong_link_target(self):
        self.links[(3, 'Answer 1.1, page 2 →', 2)] = self.links.pop(
            (3, 'Answer 1.1, page 2 →', 4)
        )
        self.assertTrue(self.problems())
        self.links[(3, 'Answer 1.1, page 2 →', 4)] = self.links.pop(
            (3, 'Answer 1.1, page 2 →', 2)
        )
        self.row_backlinks[(4, '1.1')] = ('← page 1', 1)
        self.assertTrue(self.problems())

    def test_rejects_folio_with_extra_digit(self):
        self.pages[2] = 'Answer 1.1, page 20 →'
        self.assertTrue(self.problems())

    def test_rejects_backlink_folio_with_extra_digit(self):
        self.row_backlinks[(4, '1.1')] = ('← page 10', 3)
        self.assertTrue(self.problems())

    def test_rejects_missing_backlink_when_next_answer_has_same_backlink(self):
        self.questions.append({'n': '1.2', 'page': 3, 'folio': '1'})
        self.answers.append({'n': '1.2', 'page': 4, 'folio': '2'})
        self.pages[2] += '\nAnswer 1.2, page 2 →'
        self.links[(3, 'Answer 1.2, page 2 →', 4)] = 1
        self.row_backlinks = {(4, '1.2'): ('← page 1', 3)}
        self.assertTrue(self.problems())

    def test_supports_tagged_chapter_answers(self):
        self.questions = [{'n': 'R1.1', 'page': 3, 'folio': '8'}]
        self.answers = [{'n': 'R1.1', 'page': 4, 'folio': '9'}]
        self.pages = ['', '', 'Answer R1.1, page 9 →', '']
        self.links = Counter({(3, 'Answer R1.1, page 9 →', 4): 1})
        self.row_backlinks = {(4, 'R1.1'): ('← page 8', 3)}
        self.assertIsNotNone(ANSWER_LINK.search('Answer R1.1, page 9 →'))
        self.assertIsNotNone(ANSWER_LINK.search('Answer R1.5.1, page 9 →'))
        self.assertIsNotNone(ANSWER_LINK.search('Answer A.1, page 9 →'))
        self.assertIsNotNone(ANSWER_LINK.search('Answer É.1, page 9 →'))
        self.assertFalse(self.problems())

    def test_matches_answers_heading_and_ignores_running_head_on_shared_page(self):
        questions = [{'n': '1.1', 'page': 4, 'folio': '2'}]
        answers = [{'n': '1.1', 'page': 4, 'folio': '2'}]
        pages = ['', '', '', 'Answer 1.1, page 2 →']
        xml = """<pdf2xml>
          <page number="4" width="680">
            <text top="21" left="562" width="41" height="16">Answers</text>
            <text top="161" left="55" width="20" height="19"><b>1.1</b></text>
            <text top="216" left="94" width="108" height="16"><a href="book.html#4"><b>Answer 1.1, page 2 →</b></a></text>
            <text top="299" left="55" width="67" height="25"><b>Answers</b></text>
            <text top="332" left="55" width="19" height="18"><b>1.1</b></text>
            <text top="332" left="584" width="41" height="15"><a href="book.html#4"><b>← page 2</b></a></text>
          </page>
        </pdf2xml>"""
        links, row_backlinks = parse_answer_links(xml, 'book.html', answers)
        self.assertFalse(check_answers(questions, answers, pages, links, row_backlinks))

    def test_ignores_wrapped_prompt_numbers_in_column_two(self):
        questions = [
            {'n': 'R1.1', 'page': 2, 'folio': '7'},
            {'n': 'R1.2', 'page': 3, 'folio': '8'},
            {'n': 'R1.3', 'page': 3, 'folio': '8'},
        ]
        answers = [
            {'n': 'R1.1', 'page': 4, 'folio': '9'},
            {'n': 'R1.2', 'page': 4, 'folio': '9'},
            {'n': 'R1.3', 'page': 4, 'folio': '9'},
        ]
        pages = [
            '',
            'Answer R1.1, page 9 →',
            'Answer R1.2, page 9 →\nAnswer R1.3, page 9 →',
            '',
        ]
        xml = """<pdf2xml>
          <page number="2" width="680">
            <text top="100" left="94" width="115" height="16"><a href="book.html#4">Answer R1.1, page 9 →</a></text>
          </page>
          <page number="3" width="680">
            <text top="100" left="94" width="115" height="16"><a href="book.html#4">Answer R1.2, page 9 →</a></text>
            <text top="200" left="94" width="115" height="16"><a href="book.html#4">Answer R1.3, page 9 →</a></text>
          </page>
          <page number="4" width="680">
            <text top="81" left="55" width="67" height="25"><b>Answers</b></text>
            <text top="113" left="55" width="27" height="18"><b>R1.1</b></text>
            <text top="113" left="94" width="200" height="20">Compare the behavior of</text>
            <text top="133" left="94" width="27" height="20">R1.2</text>
            <text top="153" left="94" width="27" height="20">R1.3</text>
            <text top="114" left="584" width="41" height="15"><a href="book.html#2"><b>← page 7</b></a></text>
            <text top="220" left="55" width="27" height="18"><b>R1.2</b></text>
            <text top="221" left="584" width="41" height="15"><a href="book.html#3"><b>← page 8</b></a></text>
            <text top="290" left="55" width="27" height="18"><b>R1.3</b></text>
            <text top="291" left="584" width="41" height="15"><a href="book.html#3"><b>← page 8</b></a></text>
          </page>
        </pdf2xml>"""
        links, row_backlinks = parse_answer_links(xml, 'book.html', answers)
        self.assertFalse(check_answers(questions, answers, pages, links, row_backlinks))

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
            '',
        ]
        xml = """<pdf2xml>
          <page number="2" width="680">
            <text top="100" left="94" width="115" height="16"><a href="book.html#4">Answer R1.1, page 9 →</a></text>
          </page>
          <page number="3" width="680">
            <text top="100" left="94" width="115" height="16"><a href="book.html#4">Answer R1.2, page 9 →</a></text>
          </page>
          <page number="4" width="680">
            <text top="21" left="562" width="41" height="16">Answers</text>
            <text top="81" left="55" width="67" height="25"><b>Answers</b></text>
            <text top="113" left="55" width="27" height="18"><b>R1.1</b></text>
            <text top="114" left="584" width="41" height="15"><a href="book.html#3"><b>← page 8</b></a></text>
            <text top="145" left="94" width="120" height="18">See ← page 7 in text.</text>
            <text top="200" left="55" width="27" height="18"><b>R1.2</b></text>
            <text top="201" left="584" width="41" height="15"><a href="book.html#2"><b>← page 7</b></a></text>
            <text top="232" left="94" width="120" height="18">See ← page 8 in text.</text>
          </page>
        </pdf2xml>"""
        links, row_backlinks = parse_answer_links(xml, 'book.html', answers)
        problems = check_answers(questions, answers, pages, links, row_backlinks)
        self.assertEqual(len(problems), 2)
        self.assertTrue(any('R1.1' in p for p in problems))
        self.assertTrue(any('R1.2' in p for p in problems))

        fixed_xml = """<pdf2xml>
          <page number="2" width="680">
            <text top="100" left="94" width="115" height="16"><a href="book.html#4">Answer R1.1, page 9 →</a></text>
          </page>
          <page number="3" width="680">
            <text top="100" left="94" width="115" height="16"><a href="book.html#4">Answer R1.2, page 9 →</a></text>
          </page>
          <page number="4" width="680">
            <text top="21" left="562" width="41" height="16">Answers</text>
            <text top="81" left="55" width="67" height="25"><b>Answers</b></text>
            <text top="113" left="55" width="27" height="18"><b>R1.1</b></text>
            <text top="114" left="584" width="41" height="15"><a href="book.html#2"><b>← page 7</b></a></text>
            <text top="200" left="55" width="27" height="18"><b>R1.2</b></text>
            <text top="201" left="584" width="41" height="15"><a href="book.html#3"><b>← page 8</b></a></text>
          </page>
        </pdf2xml>"""
        links_ok, row_backlinks_ok = parse_answer_links(fixed_xml, 'book.html', answers)
        self.assertFalse(check_answers(questions, answers, pages, links_ok, row_backlinks_ok))

    def test_accepts_prompt_link_next_to_valid_backlink(self):
        questions = [{'n': 'R1.1', 'page': 2, 'folio': '7'}]
        answers = [{'n': 'R1.1', 'page': 3, 'folio': '8'}]
        pages = ['', 'Answer R1.1, page 8 →', '']
        xml = """<pdf2xml>
          <page number="2" width="680">
            <text top="100" left="94" width="115" height="16"><a href="book.html#3">Answer R1.1, page 8 →</a></text>
          </page>
          <page number="3" width="680">
            <text top="81" left="55" width="67" height="25"><b>Answers</b></text>
            <text top="113" left="55" width="27" height="18"><b>R1.1</b></text>
            <text top="113" left="94" width="51" height="20"><a href="book.html#2"><i>← page 7</i></a></text>
            <text top="114" left="584" width="41" height="15"><a href="book.html#2"><b>← page 7</b></a></text>
          </page>
        </pdf2xml>"""
        links, row_backlinks = parse_answer_links(xml, 'book.html', answers)
        self.assertFalse(check_answers(questions, answers, pages, links, row_backlinks))

    def test_rejects_prompt_link_next_to_broken_backlink(self):
        questions = [{'n': 'R1.1', 'page': 2, 'folio': '7'}]
        answers = [{'n': 'R1.1', 'page': 3, 'folio': '8'}]
        pages = ['', 'Answer R1.1, page 8 →', '']
        xml = """<pdf2xml>
          <page number="2" width="680">
            <text top="100" left="94" width="115" height="16"><a href="book.html#3">Answer R1.1, page 8 →</a></text>
          </page>
          <page number="3" width="680">
            <text top="81" left="55" width="67" height="25"><b>Answers</b></text>
            <text top="113" left="55" width="27" height="18"><b>R1.1</b></text>
            <text top="113" left="94" width="51" height="20"><a href="book.html#2"><i>← page 7</i></a></text>
            <text top="114" left="525" width="100" height="15"><a href="book.html#2"><b>Broken return link</b></a></text>
          </page>
        </pdf2xml>"""
        links, row_backlinks = parse_answer_links(xml, 'book.html', answers)
        problems = check_answers(questions, answers, pages, links, row_backlinks)
        self.assertEqual(len(problems), 1)
        self.assertIn('R1.1', problems[0])

    def test_uses_asymmetric_margins_for_backlink_column(self):
        geometry = {'width': 450.0, 'inside': 50.0, 'outside': 30.0}
        questions = [
            {'n': '1.1', 'page': 2, 'folio': '1'},
            {'n': '1.2', 'page': 2, 'folio': '1'},
        ]
        answers = [
            {'n': '1.1', 'page': 3, 'folio': '2'},  # recto: right margin = outside (30) -> right_edge = 630
            {'n': '1.2', 'page': 4, 'folio': '3'},  # verso: right margin = inside (50) -> right_edge = 600
        ]
        pages = ['', 'Answer 1.1, page 2 →\nAnswer 1.2, page 3 →', '', '']
        xml = """<pdf2xml>
          <page number="2" width="675">
            <text top="100" left="45" width="115" height="16"><a href="book.html#3">Answer 1.1, page 2 →</a></text>
            <text top="150" left="45" width="115" height="16"><a href="book.html#4">Answer 1.2, page 3 →</a></text>
          </page>
          <page number="3" width="675">
            <text top="81" left="75" width="67" height="25"><b>Answers</b></text>
            <text top="113" left="75" width="20" height="18"><b>1.1</b></text>
            <text top="114" left="589" width="41" height="15"><a href="book.html#2"><b>← page 1</b></a></text>
          </page>
          <page number="4" width="675">
            <text top="113" left="45" width="20" height="18"><b>1.2</b></text>
            <text top="114" left="559" width="41" height="15"><a href="book.html#2"><b>← page 1</b></a></text>
          </page>
        </pdf2xml>"""
        links, row_backlinks = parse_answer_links(xml, 'book.html', answers, geometry)
        self.assertFalse(check_answers(questions, answers, pages, links, row_backlinks))


if __name__ == '__main__':
    unittest.main()
