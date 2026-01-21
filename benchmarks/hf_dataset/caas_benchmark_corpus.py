"""CaaS Benchmark Corpus dataset loader for Hugging Face."""

import json
import datasets


_CITATION = """
@misc{caas2026,
  author = {Imran Siddique},
  title = {Context-as-a-Service: Intelligent Context Extraction Pipeline},
  year = {2026},
  publisher = {GitHub},
  url = {https://github.com/imran-siddique/context-as-a-service}
}
"""

_DESCRIPTION = """
CaaS Benchmark Corpus v1 - A diverse collection of synthetic enterprise documents 
for benchmarking context extraction and RAG systems.
"""

_HOMEPAGE = "https://github.com/imran-siddique/context-as-a-service"
_LICENSE = "MIT"


class CaasBenchmarkCorpus(datasets.GeneratorBasedBuilder):
    """CaaS Benchmark Corpus dataset."""

    VERSION = datasets.Version("1.0.0")

    def _info(self):
        return datasets.DatasetInfo(
            description=_DESCRIPTION,
            features=datasets.Features({
                "id": datasets.Value("string"),
                "filename": datasets.Value("string"),
                "content": datasets.Value("string"),
                "format": datasets.Value("string"),
                "domain": datasets.Value("string"),
                "category": datasets.Value("string"),
                "description": datasets.Value("string"),
                "tags": datasets.Sequence(datasets.Value("string")),
                "num_lines": datasets.Value("int32"),
                "num_chars": datasets.Value("int32"),
                "estimated_tokens": datasets.Value("int32"),
                "sections": datasets.Sequence({
                    "level": datasets.Value("int32"),
                    "title": datasets.Value("string"),
                    "line": datasets.Value("int32"),
                }),
                "num_sections": datasets.Value("int32"),
                "created_at": datasets.Value("string"),
            }),
            supervised_keys=None,
            homepage=_HOMEPAGE,
            license=_LICENSE,
            citation=_CITATION,
        )

    def _split_generators(self, dl_manager):
        data_file = dl_manager.download_and_extract("data/corpus.jsonl")
        return [
            datasets.SplitGenerator(
                name=datasets.Split.TRAIN,
                gen_kwargs={"filepath": data_file},
            ),
        ]

    def _generate_examples(self, filepath):
        with open(filepath, encoding="utf-8") as f:
            for idx, line in enumerate(f):
                doc = json.loads(line)
                yield idx, doc
