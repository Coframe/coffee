<div align="center">

# Coffee &nbsp;☕ <!-- omit from toc -->

— <ins>**Cof**</ins>rame <ins>**F**</ins>ront-<ins>**E**</ins>nd <ins>**E**</ins>ngineer

*Quickly build and iterate on your front end with AI!*

<p>
<a href="https://github.com/coframe/coffee/commits"><img alt="GitHub Last Commit" src="https://img.shields.io/github/last-commit/coframe/coffee" /></a>
<a href="https://github.com/coframe/coffee/issues"><img alt="GitHub Issues" src="https://img.shields.io/github/issues/coframe/coffee" /></a>
<a href="https://github.com/coframe/coffee/blob/main/LICENSE"><img alt="License" src="https://img.shields.io/badge/License-MIT-green.svg" /></a>
<a href="https://github.com/coframe/coffee"><img alt="GitHub Repo stars" src="https://img.shields.io/github/stars/coframe/coffee?style=social" /></a>
</p>
<br />
</div>

```
<!-- TODO Animated demo of -->
<Coffee brew="Contributors.tsx" contributors={contributors}>
  Show list of contributors using circle images in horisontal line.
  On hover show name.
</Coffee>
```

> Coffee caffeinates your frontend development workflow with AI. This project is intended to be more than just a nice demo, but rather be an ergonomic tool that can write and interact with production-quality code.

- [Features](#features)
- [Try It](#try-it)
- [How It Works](#how-it-works)
- [TODO](#todo)
- [Related](#related)
- [Community](#community)
- [Core Contributors](#core-contributors)
- [License](#license)

## Features

- Works with any React codebase including Next.js, Remix, etc.
- Reliable enough for most standard UI components
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

You can also build the image yourself from this repo.

## How It Works

Coffee uses Docker to make sure that any agentic code it runs is fully isolated. Coffee is currently implemented in Python (but you don't need to touch Python to use Coffee), and the code-generation agent is relatively simple.

When you run Coffee, it will listen for changes to `js/jsx/ts/tsx` files in your source directory, and if it detects a `<Coffee>` JSX component, it will kick off its magic!

```tsx
<Coffee brew='ExampleComponent.tsx'>
  Here is where you put your prompt that Coffee will use to generate the first
  version of your desired component.
  <br />
  This is the same type of prompt that you'd use with any LLM like ChatGPT, so
  feel free to get creative and apply your favorite prompt engineering tricks.
</Coffee>
```

Every time you save your source file, Coffee will look to see if there are any `<Coffee>` components which need brewing (if they're new or if their props or prompt have been updated). For each `<Coffee>` component the agent finds, Coffee will pass your parent component code, any existing child component code (`ExampleComponent.tsx` in the above example), your prompt, and any custom configuration to the OpenAI chat completions API in order to generate a new version of the target component.

The brewing process is currently a little slow, but we're working on several ways to make it significantly faster.

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
- [ ] Add support for other popular frontend frameworks (Vue, Svelte, etc)

## Related

- [v0](https://v0.dev) - Amazing generative React playground by [Vercel](https://vercel.com)
  - We're hoping they OSS it soon in order to open it up to a wider audience 🥹
  - We were excited to experiment with a DX that was more natively integrated into a frontend developer's existing workflow, so we could better understand the tradeoffs between two approaches.
- [Screenshot to Code](https://github.com/abi/screenshot-to-code) - OSS project showcasing the power of GPT-V for UI generation 🤯
  - One of the first projects to showcase GPT-V's capabilities for UI generation from an image (besides [GDB's timeless GPT-4 announcement](https://www.youtube.com/live/outcGtbnMuQ?feature=shared&t=978), of course!)
- [Draw a UI](https://github.com/SawyerHood/draw-a-ui) - ditto!
- [Cursor](https://cursor.sh/) - AI-native IDE that the Coframe team uses and loves 🥰
  - Coffee can be used in any IDE, but we're huge fans of Cursor and are excited to see what they launch next!

## Community

Join us on [Discord](https://discord.gg/coframe) for support, to show off what you've brewed, and good vibes in general.

Follow us on [Twitter](https://twitter.com/coframe_ai) for new feature releases, product updates, and other exciting news!
 
## Core Contributors

- [Pavlo Razumovskyi](https://github.com/1um) (lead)
- [Josh Payne](https://github.com/joshpxyne)
- [Tinah Hong](https://github.com/tunahfishy)
- [Alex Korshuk](https://github.com/AlekseyKorshuk)
- [Travis Fischer](https://github.com/transitive-bullshit)

If you'd like to be a contributor, just submit a pull request!

⚡ We are also hiring for generalist engineers and AI engineers who are passionate about the future of UX/AI. Coffee is just one of the many exciting things we have brewing. If you want to build this future with us, please shoot us a DM on [Twitter](https://twitter.com/coframe_ai)!

## License

MIT © [Coframe](https://coframe.ai)
