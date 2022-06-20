---
layout: post
title:  "SED"
metadate: "hide"
categories: [ sed ]
tags: [ sed ]
image: assets/images/sed.png
---

Sed is a Stream Editor used for modifying the files in unix (or linux)

## Features of sed
#### Consider the below file for as example for our practice
<pre>$ cat file.txt 
learn about sed in unix or linux
unix commands
stream editor for linux or unix. unix is free os
unix
linux
learn os
open source
</pre>


#### Replacing or substituting string

<pre>$ sed &apos;s/unix/linux/&apos; file.txt
learn about sed in linux or linux
linux commands
stream editor for linux or linux. unix is free os
linux
linux
learn os
open source
</pre>

Here the `s` specifies the substitution operation. The `/` are delimiters. The `unix` is the search pattern and the `linux` is the replacement string.

By default, the `sed` command replaces the first occurrence of the pattern in each line and it won't replace the second, third...occurrence in the line.

#### Replacing the nth occurrence of a pattern in a line

Use the `/1`, `/2` etc flags to replace the first, second occurrence of a pattern in a line. The below command replaces the second occurrence of the word `unix` with `linux` in a line

<pre>$ sed &apos;s/unix/linux/2&apos; file.txt
learn about sed in unix or linux
unix commands
stream editor for linux or unix. linux is free os
unix
linux
learn os
open source
</pre>

<pre>$ sed &apos;s/unix/linux/1&apos; file.txt
learn about sed in linux or linux
linux commands
stream editor for linux or linux. unix is free os
linux
linux
learn os
open source
</pre>

#### Replacing all the occurrence of the pattern in a line.

The substitute flag /g (global replacement) specifies the sed command to replace all the occurrences of the string in the line.

<pre>$ sed &apos;s/unix/linux/g&apos; file.txt
learn about sed in linux or linux
linux commands
stream editor for linux or linux. linux is free os
linux
linux
learn os
open source
</pre>

#### Replacing from nth occurrence to all occurrences in a line.

Use the combination of /1, /2 etc and /g to replace all the patterns from the nth occurrence of a pattern in a line. The following sed command replaces the third, fourth, fifth... "unix" word with "linux" word in a line.

<pre>$ sed &apos;s/unix/linux/3g&apos; file.txt
learn about sed in unix or linux
unix commands
stream editor for linux or unix. unix is free os
unix
linux
learn os
open source

</pre>

#### Changing the slash (/) delimiter

You can use any delimiter other than the slash. As an example if you want to change the web url to another url as

<pre>$ cat file.txt 
learn about sed in unix or linux
unix commands
stream editor for linux or unix. unix is free os
unix
linux
learn os
open source

https://
www
http://
https://www
</pre>

<pre>$ sed &apos;s/http:\/\//www/&apos; file.txt
learn about sed in unix or linux
unix commands
stream editor for linux or unix. unix is free os
unix
linux
learn os
open source

https://
www
www
https://www
</pre>

In this case the url consists the delimiter character which we used. In that case you have to escape the slash with backslash character, otherwise the substitution won't work.

Using too many backslashes makes the sed command look awkward. In this case we can change the delimiter to another character as shown in the below example.

<pre>$ sed &apos;s|http://|www|&apos; file.txt
learn about sed in unix or linux
unix commands
stream editor for linux or unix. unix is free os
unix
linux
learn os
open source

https://
www
www
https://www
</pre>

<pre>$ sed &apos;s_http://_www_&apos; file.txt
learn about sed in unix or linux
unix commands
stream editor for linux or unix. unix is free os
unix
linux
learn os
open source

https://
www
www
https://www
</pre>

#### Using & as the matched string

There might be cases where you want to search for the pattern and replace that pattern by adding some extra characters to it. In such cases & comes in handy. The & represents the matched string.

<pre>$ sed &apos;s/unix/{&amp;}/&apos; file.txt
learn about sed in {unix} or linux
{unix} commands
stream editor for linux or {unix}. unix is free os
{unix}
linux
learn os
open source

https://
www
http://
https://www
</pre>

<pre>$ sed &apos;s/unix/{&amp;&amp;}/&apos; file.txt
learn about sed in {unixunix} or linux
{unixunix} commands
stream editor for linux or {unixunix}. unix is free os
{unixunix}
linux
learn os
open source

https://
www
http://
https://www
</pre>

#### Using \1,\2 and so on to \9

The first pair of parenthesis specified in the pattern represents the \1, the second represents the \2 and so on. The \1,\2 can be used in the replacement string to make changes to the source string. As an example, if you want to replace the word "unix" in a line with twice as the word like "unixunix" use the sed command as below.

<pre>$ sed &apos;s/\(unix\)/\1\1/&apos; file.txt
learn about sed in unixunix or linux
unixunix commands
stream editor for linux or unixunix. unix is free os
unixunix
linux
learn os
open source

https://
www
http://
https://www
</pre>

The parenthesis needs to be escaped with the backslash character. Another example is if you want to switch the words "unixlinux" as "linuxunix", the sed command is

<pre>$ sed &apos;s/\(unix\)\(linux\)/\2\1/&apos; file.txt
learn about sed in unix or linux
unix commands
stream editor for linux or unix. unix is free os
unix
linux
learn os
open source

https://
www
http://
https://www
</pre>

Another example is switching the first three characters in a line

<pre>$ sed &apos;s/^\(.\)\(.\)\(.\)/\3\2\1/&apos; file.txt
aelrn about sed in unix or linux
inux commands
rtseam editor for linux or unix. unix is free os
inux
nilux
aelrn os
epon source

tthps://
www
tthp://
tthps://www
</pre>

#### Duplicating the replaced line with /p flag

The /p print flag prints the replaced line twice on the terminal. If a line does not have the search pattern and is not replaced, then the /p prints that line only once.

<pre>$ sed &apos;s/unix/linux/p&apos; file.txt
learn about sed in linux or linux
learn about sed in linux or linux
linux commands
linux commands
stream editor for linux or linux. unix is free os
stream editor for linux or linux. unix is free os
linux
linux
linux
learn os
open source

https://
www
http://
https://www
</pre>

#### Printing only the replaced lines

Use the -n option along with the /p print flag to display only the replaced lines. Here the -n option suppresses the duplicate rows generated by the /p flag and prints the replaced lines only one time.

<pre>$ sed -n &apos;s/unix/linux/p&apos; file.txt
learn about sed in linux or linux
linux commands
stream editor for linux or linux. unix is free os
linux
</pre>

> Note : If you use -n alone without /p, then the sed does not print anything.

#### Running multiple sed commands.

You can run multiple sed commands by piping the output of one sed command as input to another sed command.

<pre>$ sed &apos;s/unix/linux/&apos; file.txt| sed &apos;s/os/system/&apos;
learn about sed in linux or linux
linux commands
stream editor for linux or linux. unix is free system
linux
linux
learn system
open source

https://
www
http://
https://www
</pre>

Sed provides -e option to run multiple sed commands in a single sed command. The above output can be achieved in a single sed command as shown below.

<pre>$ sed -e &apos;s/unix/linux/&apos; -e &apos;s/os/system/&apos; file.txt
learn about sed in linux or linux
linux commands
stream editor for linux or linux. unix is free system
linux
linux
learn system
open source

https://
www
http://
https://www
</pre>

#### Replacing string on a specific line number.

You can restrict the sed command to replace the string on a specific line number. An example is


<pre>$ sed &apos;4 s/unix/linux/&apos; file.txt
learn about sed in unix or linux
unix commands
stream editor for linux or unix. unix is free os
linux
linux
learn os
open source

https://
www
http://
https://www
</pre>

#### Replacing string on a range of lines.

You can specify a range of line numbers to the sed command for replacing a string.

<pre>$ sed &apos;1,3 s/unix/linux/&apos; file.txt
learn about sed in linux or linux
linux commands
stream editor for linux or linux. unix is free os
unix
linux
learn os
open source

https://
www
http://
https://www
</pre>

Here the sed command replaces the lines with range from 1 to 3. Another example is

<pre>$ sed &apos;2,$ s/unix/linux/&apos; file.txt
learn about sed in unix or linux
linux commands
stream editor for linux or linux. unix is free os
linux
linux
learn os
open source

https://
www
http://
https://www
</pre>

Here $ indicates the last line in the file. So the sed command replaces the text from second line to last line in the file.

#### Replace on a lines which matches a pattern.

You can specify a pattern to the sed command to match in a line. If the pattern match occurs, then only the sed command looks for the string to be replaced and if it finds, then the sed command replaces the string.

<pre>$ sed &apos;/linux/ s/unix/centos/&apos; file.txt
learn about sed in centos or linux
unix commands
stream editor for linux or centos. unix is free os
unix
linux
learn os
open source

https://
www
http://
https://www
</pre>

#### Deleting lines.
You can delete the lines a file by specifying the line number or a range or numbers.


<pre>$ sed &apos;2 d&apos; file.txt
learn about sed in unix or linux
stream editor for linux or unix. unix is free os
unix
linux
learn os
open source

https://
www
http://
https://www
</pre>

<pre>$ sed &apos;5,$ d&apos; file.txt
learn about sed in unix or linux
unix commands
stream editor for linux or unix. unix is free os
unix
</pre>

#### Duplicating lines

You can make the sed command to print each line of a file two times.

<pre>$ sed &apos;p&apos; file.txt
learn about sed in unix or linux
learn about sed in unix or linux
unix commands
unix commands
stream editor for linux or unix. unix is free os
stream editor for linux or unix. unix is free os
unix
unix
linux
linux
learn os
learn os
open source
open source


https://
https://
www
www
http://
http://
https://www
https://www
</pre>

####  Sed as grep command

You can make sed command to work as similar to grep command.

<pre>$ sed -n &apos;/unix/ p&apos; file.txt
learn about sed in unix or linux
unix commands
stream editor for linux or unix. unix is free os
unix
</pre>

Here the sed command looks for the pattern "unix" in each line of a file and prints those lines that has the pattern.

You can also make the sed command to work as grep -v, just by using the reversing the sed with NOT (!).

<pre>$ grep -v 'unix' file.txt<br>
$ sed -n &apos;/unix/ !p&apos; file.txt
linux
learn os
open source

https://
www
http://
https://www
</pre>

The ! here inverts the pattern match

#### Add a line after a match.

```bash
sed '/unix/ a "Add a new line"' file.txt
```

#### Add a line before a match

```bash
sed '/unix/ i "Add a new line"' file.txt
```

#### Add a line after a match.

```bash
sed '/unix/ a "Add a new line"' file.txt
```

####  Change a line

```bash
sed '/unix/ c "Change line"' file.txt
```

#### Transform like tr command

```bash
sed 'y/ul/UL/' file.txt
```
