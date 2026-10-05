import unittest

from ajapaik.ajapaik_comments.utils import convert_raw_urls_to_markdown


class CommentUrlConversionTests(unittest.TestCase):
    def test_raw_https_url(self):
        text = "Kas ka Suurupi?\nhttps://ajapaik.ee/photo/71006/vaade-suurupi-tuletornile/"
        converted, modified = convert_raw_urls_to_markdown(text)
        self.assertTrue(modified)
        expected = "Kas ka Suurupi?\n[https://ajapaik.ee/photo/71006/vaade-suurupi-tuletornile/](https://ajapaik.ee/photo/71006/vaade-suurupi-tuletornile/)"
        self.assertEqual(converted, expected)

    def test_raw_www_url(self):
        text = "Vaata www.geni.com/people/test"
        converted, modified = convert_raw_urls_to_markdown(text)
        self.assertTrue(modified)
        expected = "Vaata [www.geni.com/people/test](https://www.geni.com/people/test)"
        self.assertEqual(converted, expected)

    def test_trailing_punctuation(self):
        text = "Lauses punkt: https://ajapaik.ee/photo/123/. Ja koma: https://ajapaik.ee/photo/456/, vaata siit."
        converted, modified = convert_raw_urls_to_markdown(text)
        self.assertTrue(modified)
        expected = "Lauses punkt: [https://ajapaik.ee/photo/123/](https://ajapaik.ee/photo/123/). Ja koma: [https://ajapaik.ee/photo/456/](https://ajapaik.ee/photo/456/), vaata siit."
        self.assertEqual(converted, expected)

    def test_parenthesized_url(self):
        text = "(vt https://ajapaik.ee/photo/789/)"
        converted, modified = convert_raw_urls_to_markdown(text)
        self.assertTrue(modified)
        expected = "(vt [https://ajapaik.ee/photo/789/](https://ajapaik.ee/photo/789/))"
        self.assertEqual(converted, expected)

    def test_existing_markdown_link_preserved(self):
        text = "Vaata [Ajapaik](https://ajapaik.ee/photo/1/) linki."
        converted, modified = convert_raw_urls_to_markdown(text)
        self.assertFalse(modified)
        self.assertEqual(converted, text)

    def test_existing_markdown_image_preserved(self):
        text = "Siin on pilt: ![Näide](https://ajapaik.ee/thumb.jpg)"
        converted, modified = convert_raw_urls_to_markdown(text)
        self.assertFalse(modified)
        self.assertEqual(converted, text)

    def test_existing_nested_image_link_preserved(self):
        text = "Klikitav pilt: [![Pisipilt](https://ajapaik.ee/thumb.jpg)](https://ajapaik.ee/photo/1/)"
        converted, modified = convert_raw_urls_to_markdown(text)
        self.assertFalse(modified)
        self.assertEqual(converted, text)

    def test_code_block_preserved(self):
        text = "Kasuta käsku `curl https://ajapaik.ee/api/` terminalis."
        converted, modified = convert_raw_urls_to_markdown(text)
        self.assertFalse(modified)
        self.assertEqual(converted, text)

    def test_html_tag_preserved(self):
        text = '<a href="https://ajapaik.ee/">Ajapaik</a>'
        converted, modified = convert_raw_urls_to_markdown(text)
        self.assertFalse(modified)
        self.assertEqual(converted, text)

    def test_wikipedia_balanced_parentheses(self):
        text = "Vaata https://et.wikipedia.org/wiki/Tallinn_(laev) artiklit."
        converted, modified = convert_raw_urls_to_markdown(text)
        self.assertTrue(modified)
        expected = "Vaata [https://et.wikipedia.org/wiki/Tallinn_(laev)](https://et.wikipedia.org/wiki/Tallinn_(laev)) artiklit."
        self.assertEqual(converted, expected)

    def test_parenthesized_wikipedia_url(self):
        text = "(vt https://et.wikipedia.org/wiki/Tallinn_(laev))"
        converted, modified = convert_raw_urls_to_markdown(text)
        self.assertTrue(modified)
        expected = "(vt [https://et.wikipedia.org/wiki/Tallinn_(laev)](https://et.wikipedia.org/wiki/Tallinn_(laev)))"
        self.assertEqual(converted, expected)

    def test_plain_text_without_urls(self):
        text = "See on tavaline kommentaar ilma ühegi lingita."
        converted, modified = convert_raw_urls_to_markdown(text)
        self.assertFalse(modified)
        self.assertEqual(converted, text)
