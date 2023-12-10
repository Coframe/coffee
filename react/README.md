# Coffee ☕ <!-- omit from toc -->

— <ins>**Cof**</ins>rame <ins>**F**</ins>ront-<ins>**E**</ins>nd <ins>**E**</ins>ngineer

> Quickly build and iterate on React components with AI!

<p>
<a href="https://github.com/coframe/coffee/commits"><img alt="GitHub Last Commit" src="https://img.shields.io/github/last-commit/coframe/coffee" /></a>
<a href="https://github.com/coframe/coffee/issues"><img alt="GitHub Issues" src="https://img.shields.io/github/issues/coframe/coffee" /></a>
<a href="https://github.com/coframe/coffee/blob/main/LICENSE"><img alt="License" src="https://img.shields.io/badge/License-MIT-green.svg" /></a>
<a href="https://github.com/coframe/coffee"><img alt="GitHub Repo stars" src="https://img.shields.io/github/stars/coframe/coffee?style=social" /></a>
</p>

```
<!-- TODO Animated demo of -->
<Coffee brew="Contributors.tsx" contributors={contributors}>
  Show list of contributors using circle images in horisontal line.
  On hover show name.
</Coffee>
```

- [Features](#features)
- [Try It](#try-it)
- [How It Works](#how-it-works)
- [TODO](#todo)
- [Related](#related)
- [License](#license)

## Features

- Works with any React codebase including Next.js, Remix, etc.
- Realiable enough for most standard UI components
- Supports most simple prop types (data, callbacks, etc)
- Uses the same DX for both edit existing components as well as creating new components from scratch
- Generates clean, maintainable code
- This is where the future of AI-assisted code-gen is headed! 🚀

## Try It

No dependecies, no setup.

Just your React webapp normally, and then open another shell in the same directory and run:

```
docker pull coframe/coffee:latest
docker run -it -e OPENAI_API_KEY=${OPENAI_API_KEY} -v $(pwd) coframe/coffee:latest
```

## How It Works

Coffee uses Docker to make sure that any agentic code it runs is fully isolated. Coffee is currently implemented in Python (but you don't need to touch Python to use Coffee), and the code-generation agent is relatively simple.

When you run Coffee, it will listen for changes to `js/jsx/ts/tsx` files in your source directory, and if it detects a `<Coffee>` JSX component, it will kick off its magic!

```tsx
<Coffee brew='ExampleComponent.tsx' exampleProp='foo'>
  Here is where you put your prompt that Coffee will use to generate the first
  version of your desired component.
  <br />
  This is the same type of prompt that you'd use with any LLM like ChatGPT, so
  feel free to get creative and apply your favorite prompt engineering tricks.
</Coffee>
```

Every time you save your source file, Coffee will look to see if there are any `<Coffee>` components which need brewing (if they're new or if their props or prompt have been updated). For each `<Coffee>` component the agent finds, Coffee will pass your parent component code, any existing child component code (`ExampleComponent.tsx` in the above example), your prompt, and any custom configuration to the OpenAI chat completions API in order to generate a new version of the target component.

The brewing process is currently a little slow, but we're working on several ways to make it significantly faster so you can iterate on your components much faster.

Finally, once you're happy with your brewed component, you can add a `pour` prop to your `<Coffee>` component and save the file, which will automatically replace the `<Coffee>` component with the generated component.

```tsx
export function Example() {
  return (
    <Coffee
      brew='MyButton.tsx'
      title='Click Me'
      onClick={() => console.log('clicked')}
      pour
    >
      Big red button. Add generous padding and make it very noticeable.
    </Coffee>
  )
}
```

In this example, we added a special `pour` prop. When you save this file, Coffee will replace this code with the following:

```tsx
import MyButton from './MyButton'

export function Example() {
  return <MyButton title='Click Me' onClick={() => console.log('clicked')} />
}
```

Now you have a fully functional, reusable React component that's ready to use in production.

**The coolest part of Coffee, however, is that you can edit existing React components just as easily as creating new components from scratch.**

Let's say that you want to edit this button component again after the initial generation. The only difference is that you pass the path to your existing component in the `brew` prop.

```tsx
export function Example() {
  return (
    <Coffee
      brew='MyButton.tsx'
      title='Click Me'
      onClick={() => console.log('clicked')}
    >
      Make the button background fun and animated.
    </Coffee>
  )
}
```

You can keep iterating like this forever – you can never run out of Coffee! 😂

## TODO

- [ ] Add basic tests and GitHub CI
- [ ] Run `prettier` on generated code (fail gracefully if not installed)
- [ ] Variety of agents: faster/smarter/cheaper
- [ ] Add visuals and actual data to prompt (GPT-4V)
- [ ] Support custom prompt
- [ ] Support custom agents
- [ ] Expand support for `coffee.config.json` config
- [ ] Consider converting Coffee to be a native TS module
  - This would be really nice for cleanly integrating with build systems tools like Next.js, webpack, Remix, Prettier, ESlint, etc.

## Related

- [v0](https://v0.dev) - Amazing generative React playground by [Vercel](https://vercel.com)
  - We're hoping they OSS it soon and are able to open it up to a wider audience 🥹
  - We were excited to experiment with a DX that was more natively integrated into a frontend developer's existing workflow, but the two approaches each have their tradeoffs.
- [FastUI](https://github.com/pydantic/FastUI) - Generative UIs from a Python source of truth
  - Really awesome, well-done project that we took a ton of inspiration from 💯
  - One of the areas we wanted to explore that differs from FastUI's approach is that many frontend developers aren't familiar with Python, so what would a DX look like that more closely resembles how frontend devs actually build and iterate on components?

## License

MIT © [Coframe](https://coframe.ai)
