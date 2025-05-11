MCP (Model Context Protocol)

I believe the emergence of MCP is a product of prompt engineering development. More structured contextual information significantly improves model performance. When constructing prompts, we hope to provide more specific information (such as local files, databases, real-time network information, etc.) to the model, making it easier for the model to understand problems in real-world scenarios.

What would we do without MCP? We might manually filter from databases or use tools to retrieve potentially needed information, manually pasting it into prompts. As the problems we need to solve become increasingly complex, manually introducing information into prompts becomes increasingly difficult.

To overcome the limitations of manual prompts, many LLM platforms (like OpenAI, Google) have introduced function call capabilities. This mechanism allows models to call predefined functions to obtain data or perform operations when needed, significantly improving automation levels.

However, function calls also have their limitations (my understanding of function calls vs MCP may not be mature, welcome additions). I believe the key point is that function calls are highly platform-dependent, and different LLM platforms implement function call APIs quite differently. For example, OpenAI's function calling method is incompatible with Google's, requiring developers to rewrite code when switching models, increasing adaptation costs. Additionally, there are security and interactivity issues.

Data and tools exist objectively, but we hope to make the process of connecting data to models more intelligent and unified. Anthropic designed MCP based on these pain points, acting as a "universal adapter" for AI models, allowing LLMs to easily access data or call tools. More specifically, MCP's advantages include:

Ecosystem - MCP provides many ready-made plugins that your AI can use directly.
Uniformity - Not limited to specific AI models, any model supporting MCP can be flexibly switched.
Data Security - Your sensitive data stays on your computer, no need to upload everything. (Because we can design interfaces to determine which data to transmit)

3. How do users use MCP?
As users, we don't care about how MCP is implemented, we usually only consider how to use this feature more simply.

For specific usage instructions, refer to the official documentation: For Claude Desktop Users. We won't elaborate here, but after successful configuration, you can test in Claude: Can you write a poem and save it to my desktop? Claude will request your permission before creating a new file locally.

Additionally, the official team provides many ready-made MCP Servers, you just need to choose the tools you want to connect, and then integrate them.

Awesome MCP Servers
MCP Servers Website
Official MCP Servers
For example, the filesystem tool introduced by the official documentation allows Claude to read and write files, just like in a local filesystem.

4. MCP Architecture Breakdown
Let's first reference the official architecture diagram.
MCP consists of three core components: Host, Client, and Server. Let's understand how these components work together through a real scenario:

Suppose you're using Claude Desktop (Host) to ask: "What documents are on my desktop?"

Host: Claude Desktop acts as the Host, responsible for receiving your question and interacting with the Claude model.
Client: When the Claude model decides it needs to access your filesystem, the built-in MCP Client in the Host is activated. This Client is responsible for establishing connections with the appropriate MCP Server.
Server: In this example, the filesystem MCP Server is called. It's responsible for executing the actual file scanning operation, accessing your desktop directory, and returning the list of found documents.
The entire flow is like this: Your question → Claude Desktop(Host) → Claude model → Need file information → MCP Client connection → Filesystem MCP Server → Execute operation → Return results → Claude generates response → Display on Claude Desktop.

This architecture design allows Claude to flexibly call various tools and data sources in different scenarios, while developers only need to focus on developing the corresponding MCP Server without worrying about Host and Client implementation details.

5. Principle: How does the model determine tool selection?
During my learning process, I was always curious about one question: When does Claude (the model) determine which tools to use? Fortunately, Anthropic has provided us with detailed explanations:

When a user asks a question:

The client (Claude Desktop / Cursor) sends your question to Claude.
Claude analyzes available tools and decides which one(s) to use.
The client executes the selected tools through the MCP Server.
The tool execution results are sent back to Claude.
Claude combines the execution results to construct the final prompt and generates a natural language response.
The response is finally displayed to the user!

The MCP Server is actively selected and called by Claude. Interestingly, how exactly does Claude determine which tools to use? And would it use some non-existent tools (hallucinations)?
(Forgive my previous oversimplified explanation) To explore this question, let's dive into the source code. Obviously, this calling process can be divided into two steps:

The LLM (Claude) determines which MCP Servers to use.
Execute the corresponding MCP Server and reprocess the execution results.

5.1 How does the model intelligently select tools?
Let's first understand how the model determines which tools to use. Here we'll use the official MCP client example for explanation, with simplified code (removed some exception control code that doesn't affect reading logic). Through reading the code, we can see that the model determines available tools through prompts. We pass tool usage descriptions to the model in text form, allowing it to understand available tools and make selections based on real-time situations. Refer to the code comments:

[Code sections remain unchanged as they are already in English]

So where do the tool descriptions and input_schema in the code come from? Through further analysis of MCP's Python SDK source code, we can find that in most cases, when using the @mcp.tool() decorator to decorate functions, the corresponding name and description actually come directly from the user-defined function name and function docstring. Here's just a small excerpt, refer to the original code for more details.

[Code sections remain unchanged as they are already in English]

Summary: The model determines which tools to use through prompt engineering, i.e., providing structured descriptions of all tools and few-shot examples. On the other hand, Anthropic definitely did specialized training for Claude (after all, it's their own protocol, Claude better understands tool prompts and outputs structured tool call JSON code).

5.2 Tool Execution and Result Feedback Mechanism
The tool execution is actually quite simple and straightforward. Following the previous step, we send the system prompt (instructions and tool call descriptions) and user messages together to the model, then receive the model's response. When the model analyzes the user request, it will decide whether to call tools:

When no tools are needed: The model directly generates a natural language response.
When tools are needed: The model outputs a structured JSON format tool call request.
If the response contains a structured JSON format tool call request, the client will execute the corresponding tool based on this JSON code. The specific implementation logic is all in process_llm_response, the code logic is very simple.

If the model executed a tool call, the tool execution result will be sent back to the model along with the system prompt and user message, requesting the model to generate the final response.

What if there are problems with the tool call JSON code or the model has hallucinations? Through reading the code, we found that we skip invalid call requests.

Execution related code and comments are as follows:

[Code sections remain unchanged as they are already in English]

Combining this principle analysis:

Tool documentation is crucial - The model understands and selects tools through tool description text, so carefully writing tool names, docstrings, and parameter descriptions is essential.
Since MCP selection is prompt-based, any model can actually adapt to MCP as long as you can provide corresponding tool descriptions. However, when using non-Claude models, MCP usage effects and experience cannot be guaranteed (no specialized training has been done).

6. Summary
MCP (Model Context Protocol) represents the establishment of a standard for AI interaction with external tools and data. Through this article, we can understand:

The essence of MCP: It is a unified protocol standard that allows AI models to connect to various data sources and tools in a consistent way, similar to a "USB-C" interface in the AI world.
The value of MCP: It solves the platform dependency problem of traditional function calls, providing a more unified, open, secure, and flexible tool calling mechanism that benefits both users and developers.
Usage and development: For ordinary users, MCP provides rich ready-made tools that can be used without understanding any technical details; for developers, MCP provides clear architecture and SDK, making tool development relatively simple.
MCP is still in its early stages, but its potential is huge. More importantly, the ecosystem built under unified standards will positively promote the development of the entire field.

The above content has covered the basic concepts, value, and usage methods of MCP. For readers interested in technical implementation, the following appendix provides a simple MCP Server development practice to help you better understand how MCP works.

Appendix A: MCP Server Development Practice
READ⏰: 30min

After understanding MCP components, it's easy to find that for the vast majority of AI developers, we only need to care about Server implementation. Therefore, I'll introduce how to implement an MCP Server through a very simple example.

MCP servers can provide three main types of functionality:

Resources: File-like data that can be read by clients (like API responses or file contents)
Tools: Functions that can be called by LLM (requiring user approval)
Prompts: Pre-written templates to help users complete specific tasks
This tutorial will mainly focus on Tools.

A.I Best Practices for Building MCP with LLM
Before starting, Anthropic has provided us with best development practices for an LLM-based MCP Server, summarized as follows:

Introduce domain knowledge (in plain language, tell it some MCP Server development examples and materials)
Visit https://modelcontextprotocol.io/llms-full.txt and copy the complete document text. (In practice, this is too long and can be ignored)
Navigate to the MCP TypeScript SDK or Python SDK Github project and copy relevant content.
Input these as prompts in your chat conversation (as context).
Describe your requirements
What resources will your server expose
What tools will it provide
What guidance should it give
What external systems should it interact with
Give an example prompt:

... (Here is the already introduced domain knowledge)

Build an MCP server that can:

- Connect to my company's PostgreSQL database
- Expose table structures as resources
- Provide tools for running read-only SQL queries
- Include guidance for common data analysis tasks
The remaining parts are also important, but they focus more on methodology and are less practical, so I won't expand on them here. I recommend reading the official documentation directly.

A.II Manual Practice
This section mainly references the official documentation: Quick Start: For Server Developers. You can choose to skip this part directly or do a quick read.

Here I've prepared a simple example, implementing an MCP Server using Python to count the number of txt files on the current desktop and get their names (you can understand it as having little use, but it's simple enough, mainly to provide a short enough practice record for readers who have difficulty configuring the environment). The following practices are all running on my MacOS system.

[Remaining sections with steps 1-7 remain unchanged as they contain code and commands that are already in English]
