---
layout: post
title:  "Linux - sed command"
description: "Linux - sed command"
author: jinnabalu
categories: [ sed ]
image: assets/images/sed.png
featured: false
hidden: true
---

## Delete lines using sed command

In the following examples, the sed command removes the lines in file that are in a particular position in a file. 

#### Delete first line or header line

The d option in sed command is used to delete a line. The syntax for deleting a line is: 
```bash
sed 'Nd' file
```

Here N indicates Nth line in a file. In the following example, the sed command removes the first line in a file. 
```bash
sed '1d' file
unix
fedora
debian
ubuntu
```

#### Delete last line or footer line or trailer line

The following sed command is used to remove the footer line in a file. The $ indicates the last line of a file. 
```bash
sed '$d' file
linux
unix
fedora
debian
```

#### Delete particular line

This is similar to the first example. The below sed command removes the second line in a file. 
```bash
sed '2d' file
linux
fedora
debian
ubuntu
```

#### Delete range of lines

The sed command can be used to delete a range of lines. The syntax is shown below: 
```bash
sed 'm,nd' file
```

Here m and n are min and max line numbers. The sed command removes the lines from m to n in the file. The following sed command deletes the lines ranging from 2 to 4: 
```bash
sed '2,4d' file
linux
ubuntu
```

#### Delete lines other than the first line or header line

Use the negation (!) operator with d option in sed command. The following sed command removes all the lines except the header line. 
```bash
sed '1!d' file
linux
```

#### Delete lines other than last line or footer line
```bash
sed '$!d' file
ubuntu
```

#### Delete lines other than the specified range
```bash
sed '2,4!d' file
unix
fedora
debian
```

Here the sed command removes lines other than 2nd, 3rd and 4th. 

#### Delete first and last line

You can specify the list of lines you want to remove in sed command with semicolon as a delimiter. 
```bash
sed '1d;$d' file
unix
fedora
debian
```

#### Delete empty lines or blank lines
```bash
sed '/^$/d' file
```

The ^$ indicates sed command to delete empty lines. However, this sed do not remove the lines that contain spaces. 

Sed Command to Delete Lines - Based on Pattern Match

In the following examples, the sed command deletes the lines in file which match the given pattern. 

#### Delete lines that begin with specified character
```bash
sed '/^u/d' file
linux
fedora
debian
```

^ is to specify the starting of the line. Above sed command removes all the lines that start with character 'u'. 

#### Delete lines that end with specified character
```bash 
sed '/x$/d' file
fedora
debian
ubuntu
```

$ is to indicate the end of the line. The above command deletes all the lines that end with character 'x'. 

####Delete lines which are in upper case or capital letters

```bash
sed '/^[A-Z]*$/d' file
```

#### Delete lines that contain a pattern
```bash
sed '/debian/d' file
linux
unix
fedora
ubuntu
```

#### Delete lines starting from a pattern till the last line
```bash
sed '/fedora/,$d' file
linux
unix
```

Here the sed command removes the line that matches the pattern fedora and also deletes all the lines to the end of the file which appear next to this matching line. 

#### Delete last line only if it contains the pattern
```bash
sed '${/ubuntu/d;}' file
linux
unix
fedora
debian
```

Here $ indicates the last line. If you want to delete Nth line only if it contains a pattern, then in place of $ place the line number. 

Note: In all the above examples, the sed command prints the contents of the file on the unix or linux terminal by removing the lines. However the sed command does not remove the lines from the source file. To Remove the lines from the source file itself, use the -i option with sed command. 
```bash
sed -i '1d' file
```

If you don't wish to delete the lines from the original source file you can redirect the output of the sed command to another file. 
```bash
sed '1d' file > newfile
```