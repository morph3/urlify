# urlify

A very very simple tool that checks if there is an http server running on the given domains. 


# Why

Yes, there are tons of tools doing literally the same thing.

But, almost all of those shitty bugbounty tools focuses on the speed rather than the reliability. As long as you miss stuff, I don't care about how fast it sends a request. The tool should, never, miss.
 
I know that it's not the best looking code and looks pretty clunky but hey I don't care, it works and it's written in a very short amount of time.

# Examples

```
./urlify.py -l subs.txt -location -status -https -title -string API
cat subs.txt| ./urlify.py -status -title -location -https
```