![Thomas Steiner](https://web.dev/images/authors/thomassteiner.jpg)  
Thomas Steiner  
[GitHub](https://github.com/tomayac)[LinkedIn](https://www.linkedin.com/in/thomassteinerlinkedin)[Mastodon](https://toot.cafe/@tomayac)[Bluesky](https://bsky.app/profile/tomayac.com)[Homepage](https://blog.tomayac.com/)

<br />

<br />

Published: May 13, 2025

<br />

Large language models (LLMs) are notorious for their occasional lengthy responses. Even if you tell the model to answer with just "true" or "false," the model may respond with a friendly output and more than you asked for, such as: "Certainly, the answer is: true."

To address this challenge, the[Prompt API](https://developer.chrome.com/docs/ai/prompt-api)lets you specify a JSON output format of the model's response by passing a[JSON Schema](https://json-schema.org/)to the`LanguageModel.prompt()`and`LanguageModel.promptStreaming()`methods. Structured output support is available as of Chrome version 137.
| **Important** : Gemini Nano is a generative AI model. Before you build with APIs that use Gemini Nano, you should review the[People + AI Guidebook](https://pair.withgoogle.com/guidebook/)for best practices, methods, and examples for designing with AI.

## What is JSON Schema

JSON Schema is a vocabulary that enables JSON data consistency, validity, and interoperability at scale. When it comes to data exchange, JSON Schema stands out as a powerful standard for defining the structure and rules of JSON data. It uses a set of keywords to define the properties of your data.

JSON Schema is the industry standard for ensuring structured output, used, among others, by the[OpenAI API](https://platform.openai.com/docs/guides/structured-outputs?api-mode=responses#introduction)and[Gemini API](https://ai.google.dev/gemini-api/docs/structured-output?lang=rest).

For example, you prompt the model to assign at most three hashtags for a post on an online social network, such as Mastodon. The ideal output could look similar to the following JSON:  

    {
      "hashtags": [
        "#pottery",
        "#dyi"
      ] 
    }

The corresponding JSON Schema for this requested output object shape would then look as follows:  

    {
      "type": "object",
      "properties": {
        "hashtags": {
          "type": "array",
          "maxItems": 3,
          "items": {
            "type": "string",
            "pattern": "^#[^\\s#]+$"
          }
        }
      },
      "required": ["hashtags"],
      "additionalProperties": false
    }

This JSON Schema defines a structure for an object that must contain a`hashtags`field with the following constraints:

- `"type": "object"`: The root value must be a JSON object.
- `"properties": { "hashtags": ... }`: The object can (and in this case, must) have a property called`hashtags`.
- `"hashtags":`

  - `"type": "array"`: The value must be an array.
  - `"maxItems": 3`: The array can contain at most 3 items.
  - `"items": { "type": "string", "pattern": "^#[^\\s#]+$" }`: Each item in the array must be a string that matches the given regular expression pattern:`^#[^\\s#]+$`:
    - `^#`→ must start with a`#`.
    - `[^\\s#]+`→ followed by one or more characters that are not a space (`\s`) or another`#`.
    - `$`→ must end there.
- `"required": ["hashtags"]`: The object must contain the`hashtags`property.

- `"additionalProperties": false`: No other properties than hashtags are allowed.

Read the[JSON Schema Basics](https://json-schema.org/understanding-json-schema/basics)documentation for a complete description of the format's capabilities.

In fact, LLMs are really good at creating JSON Schema. Describe the constraints in natural language in your prompt and provide a valid example JSON object, and you're halfway there. You can then validate JSON objects against the generated JSON Schema with one of the[JSON Schema validators](https://json-schema.org/tools?query&sortBy=name&sortOrder=ascending&groupBy=toolingTypes&licenses&languages&drafts&toolingTypes&environments&showObsolete=false#validator), for example, the online[Newtonsoft JSON Schema Validator](https://www.jsonschemavalidator.net/).

![Successfully validating a JSON object against a JSON Schema in a JSON Schema validator.](https://developer.chrome.com/static/docs/ai/structured-output-for-prompt-api/json-schema-validator.png)

## Pass a JSON Schema to the Prompt API

To make sure the model respects a requested JSON Schema, you need to pass the JSON Schema as an argument to the`prompt()`or the`promptStreaming()`methods' options object as the value of a`responseConstraint`field.

Here's a very basic JSON Schema example that makes sure the model responds with either`true`or`false`in classifying whether a given message like this[Mastodon post](https://front-end.social/@mia/114383365215723684)is about pottery.  

    const session = await LanguageModel.create();

    const schema = {
      "type": "boolean"
    };

    const post = "Mugs and ramen bowls, both a bit smaller than intended- but that's
    how it goes with reclaim. Glaze crawled the first time around, but pretty happy
    with it after refiring.";

    const result = await session.prompt(  
      `Is this post about pottery?\n\n${post}`,
      {  
        responseConstraint: schema,
      }
    );
    console.log(JSON.parse(result));
    // true

## Support predictable outputs

Structured output support for the Prompt API makes the responses of the LLM a lot more predictable. Rather than extracting an object from a Markdown response or other post-processing, developers can now assume the model's response is valid JSON.

This brings built-in AI one step closer to cloud-based APIs, with all the benefits of running local, client-side AI.