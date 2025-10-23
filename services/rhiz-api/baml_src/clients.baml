// BAML Client Configuration for Rhiz Protocol
// Manages LLM provider connections with fallback support

client<llm> GPT4 {
  provider openai
  options {
    model gpt-4-turbo-preview
    api_key env.OPENAI_API_KEY
    temperature 0.7
    max_tokens 2000
  }
}

client<llm> GPT4Mini {
  provider openai
  options {
    model gpt-4o-mini
    api_key env.OPENAI_API_KEY
    temperature 0.7
    max_tokens 1500
  }
}

client<llm> GPT35 {
  provider openai
  options {
    model gpt-3.5-turbo
    api_key env.OPENAI_API_KEY
    temperature 0.7
    max_tokens 1000
  }
}

// Retry strategy for production reliability
retry_policy StandardRetry {
  max_retries 3
  strategy {
    type exponential_backoff
    delay_ms 1000
    multiplier 2
  }
}

