---

From Natural Language to Cloud Infrastructure
Building an MCP-powered AWS automation agent (V1)

A few weeks ago, I was obsessed with one question:
“Can a machine reliably turn natural language into something deterministic?”

That question led me to build my first NL2SQL system. It worked… surprisingly well. This time, though, the question was bigger — and honestly, a little scarier:

Can natural language set up real infrastructure?

Not a mock.
Not a plan.
Actual AWS resources.

This blog is about Version 1 of that attempt.

And for the first time, it wasn’t a solo experiment.

---

The Idea: Infra Setup Without Touching the Console

Anyone who has set up cloud infrastructure knows the drill.

You read documentation that assumes you already know what you’re doing.
You search StackOverflow for that one missing parameter.
You miss a flag.
You destroy and recreate.
You repeat until it somehow works.

We found ourselves asking:

What if you could just say:
“Create a t2.micro EC2 instance connected to S3”

…and the system figured out what that actually means, and then did it?

No digging through pages of documentation.
No clicking around the AWS console.
No YAML or Terraform files for simple setups.

Just intent turning into execution.

---

Why This Is Harder Than NL2SQL

NL2SQL felt hard. This felt harder.

Here’s why.

SQL is constrained — the output space is relatively small.
Infrastructure is stateful — every action permanently changes the environment.
The blast radius is real.
One wrong call means things break, or cost money.

By stateful, I mean this: once you create, modify, or delete infrastructure, the system now exists in a new state. There’s no “just regenerate the answer” the way there is with text or queries. Mistakes don’t disappear when the chat resets.

That changes everything.

To make this even remotely viable, we realized we needed three things.

Up-to-date AWS knowledge.
A way for the model to figure out what it doesn’t know.
Execution that’s inspectable, not magical.

That’s when MCP — the Model Context Protocol — entered the picture.

---

Architecture: How V1 Works

At a high level, Version 1 looks like this:

Natural language → LLM → MCP tools → AWS SDK

Simple on paper. Surprisingly subtle in practice.

The devil, as always, is in the glue.

---

An MCP Server That Understands AWS (On Demand)

Instead of assuming the model “knows AWS,” we built an MCP server that can scrape official boto3 documentation, cache it as structured JSON, expose it to the model as queryable resources, and refresh those resources when they become stale.

So instead of hoping the model is correct, we force it to check first.

Before doing anything destructive, the system effectively asks:

“Do I actually have the documentation needed to answer this?”

If it doesn’t, it scrapes the docs on the fly.

No embeddings.
No fine-tuning.
No prompt gymnastics.

Just live, inspectable grounding from the source of truth.

---

A Strict Tool-Driven Workflow (No YOLO Calls)

One thing we learned very quickly:

If you don’t constrain a language model, it will hallucinate with confidence.

That’s fine for brainstorming. It’s dangerous for infrastructure.

So we imposed a strict workflow.

First, detect which AWS services are involved.
Then, check whether documentation exists for them.
Next, fetch the available SDK methods.
Only then execute an operation.

This changes the role of the LLM from a creative text generator into a planner and dispatcher.

Which is exactly what you want when interacting with systems that have real side effects.

---

A Chat UI That Shows Every Decision

We wrapped the whole thing in a chat interface, not just for convenience, but for visibility.

The UI lets you see responses stream in, watch every tool call the model makes, inspect parameters before execution, and see AWS responses inline.

Nothing happens silently.
Nothing is hidden behind abstractions.

If something breaks, you can trace it back step by step.

That transparency turned out to be essential — for both debugging and trust.

---

What Works (Surprisingly Well)

For a V1, a few things genuinely exceeded our expectations.

The model is very good at mapping intent to AWS services.
On-demand documentation scraping dramatically reduces stale knowledge issues.
MCP makes tools feel composable, not bolted on.
Watching real infrastructure get created from a sentence is… surreal.

There’s a moment where you hit enter and think:

“Oh. This could actually replace a lot of manual setup.”

That’s an exciting realization.
It’s also a slightly dangerous one.

---

What Definitely Doesn’t (Yet)

Let’s be honest — this is not production-ready.

Some very real gaps.

There are no explicit approval gates before execution.
There’s no cost estimation before spinning things up.
There’s no rollback or drift handling.
Documentation scraping is fragile.
Security guardrails are minimal.

At this stage, this is a power tool, not a safety tool.

And that’s okay.

Version 1 wasn’t about solving everything.
It was about answering a simpler question.

Is natural language even a viable interface for infrastructure?

---

Why This Time Was Different

Unlike my NL2SQL project, this wasn’t a solo rabbit hole.

This project was built with a close friend, and that mattered more than I expected.

Infrastructure automation isn’t forgiving. Design decisions compound. Safety matters. Architecture matters. There’s no such thing as “just a hack” when real systems are involved.

Having another person in the loop forced better thinking about failure modes, observability, and long-term direction.

For the first time, this felt less like an experiment and more like the start of a system.

---

Where This Is Going

The obvious next step — and the real goal — is this:

From architecture diagrams to live infrastructure.

The idea is simple to say and very hard to build.

Imagine uploading a diagram and having the system understand components, infer networking and dependencies, choose sane defaults, provision everything, and explain exactly what it did.

That’s not V1.

But V1 is how you get there.

---

Final Thoughts

Natural language is not a replacement for engineering judgement.

But it can be an interface to it.

Just like NL2SQL wasn’t about eliminating SQL, this isn’t about replacing Terraform or cloud expertise.

It’s about lifting the starting point — reducing friction between intent and execution.

And honestly?

Watching real cloud resources spin up because of a sentence still feels a little unreal.

Which is usually a good sign you’re onto something.

---