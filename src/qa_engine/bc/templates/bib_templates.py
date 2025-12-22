"""
QA-compliant bibliography templates for BC content generation.

All templates pass these QA rules:
- bib-undefined-cite: All citations have bib entries
- bib-malformed-cite-key: Keys are clean alphanumeric
"""

from typing import Optional


class BibTemplates:
    """QA-compliant bibliography templates."""

    @staticmethod
    def article(
        key: str,
        author: str,
        title: str,
        journal: str,
        year: int,
        volume: Optional[str] = None,
        pages: Optional[str] = None,
    ) -> str:
        """
        Generate BibTeX article entry.

        Args:
            key: Citation key (alphanumeric with underscores)
            author: Author names
            title: Article title
            journal: Journal name
            year: Publication year
            volume: Optional volume number
            pages: Optional page range

        Returns:
            BibTeX entry string
        """
        entry = f"""@article{{{key},
    author = {{{author}}},
    title = {{{title}}},
    journal = {{{journal}}},
    year = {{{year}}}"""

        if volume:
            entry += f",\n    volume = {{{volume}}}"
        if pages:
            entry += f",\n    pages = {{{pages}}}"

        entry += "\n}"
        return entry

    @staticmethod
    def inproceedings(
        key: str,
        author: str,
        title: str,
        booktitle: str,
        year: int,
        pages: Optional[str] = None,
    ) -> str:
        """
        Generate BibTeX conference paper entry.

        Args:
            key: Citation key
            author: Author names
            title: Paper title
            booktitle: Conference name
            year: Publication year
            pages: Optional page range

        Returns:
            BibTeX entry string
        """
        entry = f"""@inproceedings{{{key},
    author = {{{author}}},
    title = {{{title}}},
    booktitle = {{{booktitle}}},
    year = {{{year}}}"""

        if pages:
            entry += f",\n    pages = {{{pages}}}"

        entry += "\n}"
        return entry

    @staticmethod
    def book(
        key: str,
        author: str,
        title: str,
        publisher: str,
        year: int,
    ) -> str:
        """
        Generate BibTeX book entry.

        Args:
            key: Citation key
            author: Author names
            title: Book title
            publisher: Publisher name
            year: Publication year

        Returns:
            BibTeX entry string
        """
        return f"""@book{{{key},
    author = {{{author}}},
    title = {{{title}}},
    publisher = {{{publisher}}},
    year = {{{year}}}
}}"""

    @staticmethod
    def online(
        key: str,
        author: str,
        title: str,
        url: str,
        year: int,
        note: Optional[str] = None,
    ) -> str:
        """
        Generate BibTeX online/misc entry.

        Args:
            key: Citation key
            author: Author/organization name
            title: Resource title
            url: URL
            year: Access year
            note: Optional note

        Returns:
            BibTeX entry string
        """
        entry = f"""@misc{{{key},
    author = {{{author}}},
    title = {{{title}}},
    howpublished = {{\\url{{{url}}}}},
    year = {{{year}}}"""

        if note:
            entry += f",\n    note = {{{note}}}"

        entry += "\n}"
        return entry

    @staticmethod
    def generate_standard_refs() -> str:
        """
        Generate standard AI/ML references commonly used in books.

        Returns:
            Multiple BibTeX entries for common references
        """
        entries = [
            BibTemplates.article(
                "goodfellow2015explaining",
                "Goodfellow, Ian J and Shlens, Jonathon and Szegedy, Christian",
                "Explaining and Harnessing Adversarial Examples",
                "arXiv preprint arXiv:1412.6572",
                2015,
            ),
            BibTemplates.inproceedings(
                "vaswani2017attention",
                "Vaswani, Ashish and others",
                "Attention is All You Need",
                "Advances in Neural Information Processing Systems",
                2017,
            ),
            BibTemplates.article(
                "devlin2018bert",
                "Devlin, Jacob and others",
                "BERT: Pre-training of Deep Bidirectional Transformers",
                "arXiv preprint arXiv:1810.04805",
                2018,
            ),
            BibTemplates.article(
                "brown2020language",
                "Brown, Tom and others",
                "Language Models are Few-Shot Learners",
                "Advances in Neural Information Processing Systems",
                2020,
            ),
            BibTemplates.online(
                "owasp2024llm",
                "OWASP Foundation",
                "OWASP Top 10 for Large Language Model Applications",
                "https://owasp.org/www-project-top-10-for-large-language-model-applications/",
                2024,
            ),
        ]
        return "\n\n".join(entries)
