# stack-ide-sublime

Sublime Text plugin for [stack-ide](https://github.com/commercialhaskell/stack-ide)

**Bleeding edge note:** 
Requires `stack` 0.1.2+, `stack-ide` 0.1+, `ide-backend` HEAD and GHC 7.10+.

`stack-ide-sublime` also requires for the moment that you are opening the same folder that holds the `.cabal` file, and that the folder is named the same as the `.cabal` file.

### Install instructions

First make sure to install [stack](https://github.com/commercialhaskell/stack#user-content-how-to-install)
and [stack-ide](https://github.com/commercialhaskell/stack-ide).

**On OSX** install this package with the following command:
`(cd "~/Library/Application Support/Sublime Text 3/Packages"; git clone https://github.com/lukexi/stack-ide-sublime.git)`

**On Linux** install this package with the following command:
`(cd ~/.config/sublime-text-3/Packages; git clone https://github.com/lukexi/stack-ide-sublime.git)`


### Screenshots

![SublimeStackIDE Errors](http://lukexi.github.io/RawhideErrors.png)
![SublimeStackIDE Autocomplete](http://lukexi.github.io/RawhideAutocomplete.png)
![SublimeStackIDE Type-at-cursor](http://lukexi.github.io/RawhideTypeAtCursor.png)


### Troubleshooting
First check the Sublime Text console with `ctrl-``. You can increase the plugin's log level by changing the "verbosity" setting in SublimeStackIDE.sublime-settings to "debug". Let us know what you see and we'll get it fixed.