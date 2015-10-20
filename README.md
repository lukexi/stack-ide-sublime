
![build status](https://travis-ci.org/lukexi/stack-ide-sublime.svg)
[![Coverage Status](https://coveralls.io/repos/tomv564/stack-ide-sublime/badge.svg?branch=extract_parsing&service=github)](https://coveralls.io/github/tomv564/stack-ide-sublime?branch=extract_parsing)

# stack-ide-sublime

Sublime Text plugin for [stack-ide](https://github.com/commercialhaskell/stack-ide)

**Bleeding edge note:**
Requires `stack` 0.1.6+, `stack-ide` 0.1+, `ide-backend` HEAD and GHC 7.10+.

`stack-ide-sublime` also requires for the moment that you are opening the same folder that holds the `.cabal` file, and that the folder is named the same as the `.cabal` file.

### Install instructions

First make sure to install [stack](https://github.com/commercialhaskell/stack#user-content-how-to-install)
and [stack-ide](https://github.com/commercialhaskell/stack-ide).

**On OSX** install this package with the following command:
`(cd "~/Library/Application Support/Sublime Text 3/Packages"; git clone https://github.com/lukexi/stack-ide-sublime.git SublimeStackIDE)`

**On Linux** install this package with the following command:
`(cd ~/.config/sublime-text-3/Packages; git clone https://github.com/lukexi/stack-ide-sublime.git SublimeStackIDE)`

**On Windows** install this package with the following command:
`(cd $APPDATA/Sublime\ Text\ 3/Packages/; git clone https://github.com/lukexi/stack-ide-sublime.git SublimeStackIDE)`


### Screenshots

![SublimeStackIDE Errors](http://lukexi.github.io/RawhideErrors.png)
![SublimeStackIDE Autocomplete](http://lukexi.github.io/RawhideAutocomplete.png)
![SublimeStackIDE Type-at-cursor](http://lukexi.github.io/RawhideTypeAtCursor.png)


### Tips

#### Hide stack-ide generated folders from Sublime Text

Add the following to your global User Preferences *(Sublime Text -> Preferences -> Settings - User)*:

`"folder_exclude_patterns": [".git", ".svn", "CVS", ".stack-work", "session.*"],`


### Troubleshooting

First check the Sublime Text console with `ctrl-``. You can increase the plugin's log level by changing the "verbosity" setting in SublimeStackIDE.sublime-settings to "debug". Let us know what you see and we'll get it fixed.

#### Known issues

##### Not working in executable targets

Add modules (eg. Main) to the executable target's `other_modules` list in the cabal file. After restarting Stack IDE you should see the listed modules being compiled (see https://github.com/commercialhaskell/stack-ide/issues/28)

##### Error "can't find file: /Users/myself/first-project/Lib" in the console

This was a problem in stack 1.3, upgrade to a newer version (see: https://github.com/lukexi/stack-ide-sublime/issues/13)

