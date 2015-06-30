```
=~=~=~=~=~=~=~=~=~=~=~=~=~=~=~
.-,--.           .       .     
 `|__/ ,-. . , , |-. . ,-| ,-. 
  | \  ,-| |/|/  | | | | | |-' 
`-'  ` `-^ ' '   ' ' ' `-' `-' 
=~=~=~=~=~=~=~=~=~=~=~=~=~=~=~
```


![Rawhide Errors](http://lukexi.github.io/RawhideErrors.png)
![Rawhide Autocomplete](http://lukexi.github.io/RawhideAutocomplete.png)
![Rawhide Type-at-cursor](http://lukexi.github.io/RawhideTypeAtCursor.png)




An Sublime Text IDE for Haskell based on

https://github.com/fpco/ide-backend

via

https://github.com/chrisdone/ide-backend-client

Clone to
`~/Library/Application Support/Sublime Text 3/Packages/Rawhide`

Bleeding edge notes:
Currently depends on some patches in https://github.com/lukexi/ide-backend-client,
which in turn depends on the newest https://github.com/fpco/ide-backend.
Clone them both, and then run (assuming you're in directory you cloned them both into):
```
cabal install ide-backend/ide-backend-common/
cabal install ide-backend/ide-backend-server/
cabal install ide-backend/ide-backend-rts/
cabal install ide-backend/ide-backend/
cabal install ide-backend-client/ide-backend-json/
cabal install ide-backend-client/ide-backend-client/
```
Rawhide currently expects you to open a folder in sublime with a .cabal file in it.
Stack support is underway.
