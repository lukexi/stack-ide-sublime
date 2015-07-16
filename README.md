# stack-ide-sublime

Sublime Text plugin for [stack-ide](https://github.com/commercialhaskell/stack-ide)

**Bleeding edge note:** 
Requires `stack` 0.1.2+, `stack-ide` 0.1+ and GHC 7.10+.
The current version of `ide-backend` has a limitation that you must have the `ide-backend-rts` package available in your `stack.yaml` file; otherwise you'll see an error panel saying `Couldn't find package: ide-backend-rts` when opening a project with `stack-ide-sublime`. You can work around this by adding `/my/code/checkouts/ide-backend/ide-backend-rts` to each project's `stack.yaml` under `packages`. There's a pull request that will be merged any moment now to fix this here: https://github.com/fpco/ide-backend/pull/290.

`stack-ide-sublime` also requires for the moment that you are opening the same folder that holds the `.cabal` file, and that the folder is named the same as the `.cabal` file.

### Install instructions

First make sure to install [stack](https://github.com/commercialhaskell/stack#user-content-how-to-install)
and [stack-ide](https://github.com/commercialhaskell/stack-ide).

**On OSX** clone this package to:
`~/Library/Application Support/Sublime Text 3/Packages/SublimeStackIDE`

**On Linux** install this package with the following command:
`(cd ~/.config/sublime-text-3/Packages; git clone https://github.com/lukexi/stack-ide-sublime.git)`


### Screenshots

![SublimeStackIDE Errors](http://lukexi.github.io/RawhideErrors.png)
![SublimeStackIDE Autocomplete](http://lukexi.github.io/RawhideAutocomplete.png)
![SublimeStackIDE Type-at-cursor](http://lukexi.github.io/RawhideTypeAtCursor.png)


