"""Source-relevance instructions and the Qwen yes/no scoring template."""

SOURCE_RELEVANCE_INSTRUCTION = (
    "Retrieve cited source passages relevant to the query. For a product description, "
    "find matching tariff descriptions using their source hierarchy. For a legal question, "
    "find the source provisions that answer it. Do not assume unstated product attributes."
)

DEFAULT_QWEN_INSTRUCTION = (
    "Retrieve the tariff entry whose cited description and hierarchy "
    "match the product described in the query."
)

RERANK_PROMPT_VERSION = "source-relevance-v1"

QWEN_PROMPT_PREFIX = (
    "<|im_start|>system\n"
    "Judge whether the Document meets the requirements based on the Query and the Instruct provided. "
    'Note that the answer can only be "yes" or "no".'
    "<|im_end|>\n<|im_start|>user\n"
)
QWEN_PROMPT_SUFFIX = "<|im_end|>\n<|im_start|>assistant\n<think>\n\n</think>\n\n"
QWEN_PAIR_TEMPLATE = "<Instruct>: {instruction}\n<Query>: {query}\n<Document>: {document}"


def format_qwen_prompt(query: str, document: str, instruction: str | None = None) -> str:
    return (
        QWEN_PROMPT_PREFIX
        + QWEN_PAIR_TEMPLATE.format(
            instruction=instruction or DEFAULT_QWEN_INSTRUCTION, query=query, document=document
        )
        + QWEN_PROMPT_SUFFIX
    )
