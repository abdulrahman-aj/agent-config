// A two-chapter sample that exercises every part of the template's interface.
// Build: python3 ../build.py book.typ
#import "template.typ": *

#show: book.with(
  title: "Inside .git",
  subtitle: [What a commit is made of, and how to get one back after you lose it.],
  reader: [Written for a developer who uses Git daily and has never opened `.git`],
  snapshot: [Every command was run with Git 2.56.1 on 2026-11-17, in a fresh repository
    with author and dates pinned so the ids in this book match yours.],
)

#chapter("Before you start", numbered: false)[
You will need a terminal and Git. Each exercise starts in an empty scratch directory, so
nothing here touches a repository you care about. Set the same author and date as this
book and every object id you see will match the printed ones:

```terminal
$ export GIT_AUTHOR_NAME=Ada GIT_AUTHOR_EMAIL=ada@example.com \
  GIT_COMMITTER_NAME=Ada GIT_COMMITTER_EMAIL=ada@example.com \
  GIT_AUTHOR_DATE=2026-11-17T09:00:00Z GIT_COMMITTER_DATE=2026-11-17T09:00:00Z
$ mkdir scratch && cd scratch && git init -q -b main
```
]

#chapter("Three kinds of object", label: <ch-objects>)[
#takeaways[
  - read any commit, tree or file straight from Git's object store;
  - predict which ids change when you edit a file, and explain why.
]

Git stores your history as files named by a hash of their contents. Once you can read
those files you no longer need to trust what a porcelain command prints about them.

== Blobs: file contents with no name

A _blob_ holds a file's bytes and nothing else: no name, no permissions, no date. Its id is
the SHA-1 of a short header plus those bytes, so two files with the same contents share one
blob, whatever they are called.

```terminal
$ echo 'hello' > greeting.txt
$ git hash-object greeting.txt
>> ce013625030ba8dba906f756967f9e9ca394464a
```

The header is the word `blob`, the size in bytes and a NUL. Python's standard library
gives the same id, which is the whole trick:

```python
import hashlib

data = b"hello\n"
header = b"blob %d\0" % len(data)
print(hashlib.sha1(header + data).hexdigest())
```

== Trees and commits

A _tree_ maps names to blobs and to other trees; it is a directory listing. A _commit_
points at one tree, the snapshot, and at its parent commits, plus author and message. The
chain runs one way: a commit knows its parent, a parent never knows its children.

#diagram("objects.svg")[The repository after the first commit. A branch is a file holding a
commit id; the commit names a tree, and the tree names blobs.]

```terminal
$ git add greeting.txt && git commit -qm 'Add greeting'
$ git cat-file -p HEAD
tree 57e9529754dc514a3ec10db2ff882018fbe1fcbf
author Ada <ada@example.com> 1794906000 +0000
committer Ada <ada@example.com> 1794906000 +0000

Add greeting
$ git cat-file -p HEAD^{tree}
>> 100644 blob ce013625030ba8dba906f756967f9e9ca394464a	greeting.txt
```

The blob id in the tree is the one `hash-object` printed before the commit existed. Git did
not copy the file; it computed the same name for the same bytes.

#table(columns: (auto, 1fr, 1fr),
  [Object], [Holds], [Changes when],
  [blob], [file bytes], [the bytes change],
  [tree], [names, modes, and the ids of blobs and trees], [any entry below it changes],
  [commit], [a tree id, parent ids, author, message], [its tree, parents, message or
    timestamps change],
)

#exercise("Watch one edit ripple upward", where: "Your machine")[
In your scratch repository, append a line to `greeting.txt`, commit, and print the new
commit and its tree with `git cat-file -p`. Before you look, write down which of the three
ids (blob, tree, commit) you expect to change. Then compare.
]

#question[You rename `greeting.txt` to `hello.txt` without changing its contents and
commit. Which objects does Git write?][A new tree and a new commit. The blob is reused: its
id depends only on the bytes, and the name lives in the tree.]

#question[A colleague says Git "stores diffs between versions". What would you run to
show them what it stores, and what would it show?][`git cat-file -p` on a commit, then on
its tree: the tree lists whole blobs, not changes. Packfiles do delta-compress objects
on disk, but that is storage, invisible at this level.]
]

#chapter("Losing a commit and getting it back", label: <ch-refs>)[
#takeaways[
  - tell from the reflog whether "lost" work is recoverable;
  - recover it, and know how long you have.
]

== Branches are files

A _ref_ is a name for a commit id. A branch is a ref stored in `.git/refs/heads/`, one
line of text:

```terminal
$ cat .git/refs/heads/main
36b93bb746927ae09afb3b512056f95a7f099214
```

Moving a branch rewrites that line. The commit it pointed at stays in the object store
until garbage collection decides nothing needs it.

== The reflog

Every time `HEAD` moves, Git appends the old and new ids to the _reflog_. Here a second
commit is made and then thrown away with `reset --hard`:

```terminal
$ echo 'hi' >> greeting.txt
$ git commit -qam 'Extend greeting'
$ git reset --hard HEAD~1
HEAD is now at 36b93bb Add greeting
$ git reflog
36b93bb HEAD@{0}: reset: moving to HEAD~1
>> 3428417 HEAD@{1}: commit: Extend greeting
36b93bb HEAD@{2}: commit (initial): Add greeting
```

No branch names `3428417` any more, but the reflog does, and an object that any reflog
entry names counts as reachable. Recovery is one command:
`git branch rescue 3428417`.

#exercise("Make garbage collection take it", where: "Scratch repository", disposable: true)[
Do this only in the scratch repository. Delete the rescue branch if you made one, expire the reflog, and
collect garbage now instead of on Git's schedule:

```terminal
$ git branch -D rescue
$ git reflog expire --expire-unreachable=now --all
$ git gc --prune=now -q
$ git cat-file -t 3428417
fatal: Not a valid object name 3428417
```

Two separate steps had to happen: the reflog entry expired, then `gc` deleted the
unreachable object. On a normal repository the first step waits 30 days for unreachable
entries (`gc.reflogExpireUnreachable`).
]

#aside[Each branch has its own reflog too, under `.git/logs/refs/heads/`. Both are local:
a fresh clone starts with empty reflogs, and pushing never sends them.]

#case("The force-push on Friday", meta: [Reproduced in a scratch repository])[
On Friday afternoon a teammate ran `git reset --hard HEAD~3` on `main`, then
`git push --force`. Three commits by two other people disappeared from the server's
`main`. On Monday the teammate says the work is gone for good because the server has no
reflog. One of the two authors still has a clone they last pulled on Thursday.
][Is the work gone? What would you do first?][
No. The Thursday clone has all three commits: they are reachable from its own
`origin/main` and `main`, which have not moved since. First, ask that author not to pull
or fetch. Then have them push those commits to a new branch on the server, and review
before anyone moves `main` back. The teammate was right that the server's reflog would not
help; a hosted remote gives you no reflog to run. They were wrong that it mattered.
]

#question[`git reflog` shows the commit you want, 45 days old, reached only through
`HEAD@{57}`. Is it still safe to wait until tomorrow to recover it?][Not by default. Entries
for unreachable commits expire after 30 days, so this one survives only because nothing
has run `gc` with expiry since, and the next automatic `gc` may delete it. Branch it now.]
]

#chapter("Glossary", numbered: false)[
#glossary(
  ([blob], [A file's contents, named by their hash. No name or mode.], <ch-objects>),
  ([commit], [A tree, its parents, an author and a message.], <ch-objects>),
  ([ref], [A name for a commit id, such as a branch.], <ch-refs>),
  ([reflog], [The local log of where `HEAD` and each branch pointed.], <ch-refs>),
  ([tree], [A directory listing: names mapped to blobs and trees.], <ch-objects>),
)
]
