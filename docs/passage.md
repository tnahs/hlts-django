```
<text>
    user:
        object: <user>
        relation: ForeignKey
    uuid: uuid

    body: text
    notes: string
    source:
        object: <source>
        relation: ForeignKey
    tags:
        objects: <tag>
        relation: ManyToMany
    collections:
        objects: <collection>
        relation: ManyToMany
    origin:
        object: <origin>
        relation: ForeignKey
    date_created: datetime
    date_modified: datetime

    is_starred: bool
    in_trash: bool

    topics:
        objects: <topic>
        relation: ManyToMany
    count_read: int
    count_query: int

    is_refreshable: bool

<source>
    user:
        object: <user>
        relation: ForeignKey

    name: string
    individuals:
        objects: <individual>
        relation: ManyToMany
    url: url
    date: datetime
    notes: string
    date_created: datetime
    date_modified: datetime

<individual>
    user:
        object: <user>
        relation: ForeignKey

    name: string
    aka:
        objects: <individual>
        relation: ManyToMany
    date_created: datetime
    date_modified: datetime

<collection>
    user:
        object: <user>
        relation: ForeignKey

    name: string
    color: string
    pinned: bool
    description: string
    date_created: datetime
    date_modified: datetime

<tag>
    user:
        object: <user>
        relation: ForeignKey

    name: string
    color: string
    description: string
    pinned: bool
    date_created: datetime
    date_modified: datetime

<topic>
    user:
        object: <user>
        relation: ForeignKey

    name: string
    date_created: datetime
    date_modified: datetime

<medium>
    user:
        object: <user>
        relation: ForeignKey

    name: string

<origin>
    user:
        object: <user>
        relation: ForeignKey

    name: string
    date_created: datetime
    date_modified: datetime
```