# Coffee ☕

— <ins>**Cof**</ins>rame <ins>**F**</ins>ront-<ins>**E**</ins>nd <ins>**E**</ins>ngineer

Quickly build and iterate on react components with LLM:
```
<!-- TODO Animated demo of -->
<Coffee brew="Contributors.tsx" contributors={contributors}>
   Show list of contributors using circle images in horisontal line.
   On hover show name.
</Coffee>
```

# Try it:
No dependecies, no setup:
```
docker pull coframe/coffee:latest
docker run -it -e OPENAI_API_KEY=${OPENAI_API_KEY} -v $(pwd):/frontend_dir coframe/coffee:latest
```

# Customize:
Create `coffee.config.json` with:
```json
{
    ...setup...
}
```


# How to:
* Edit existing component
* Extract code to component
* Create own prompt
* Create own agent


# TODO:
* Prettier
* Variaty of agents: faster/smarter/cheaper
* Visual and data feedback loop
* DSL
