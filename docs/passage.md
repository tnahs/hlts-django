```
<passage>
    owner:
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
    related:
        objects: <passage>
        relation: ManyToMany
    count_read: int
    count_query: int

    is_refreshable: bool

<source>
    owner:
        object: <user>
        relation: ForeignKey

    name: string
    authors:
        objects: <author>
        relation: ManyToMany
    publication:
    url: url
    date: datetime
    notes: string
    medium:
        object: <medium>
        relation: ForeignKey
    date_created: datetime
    date_modified: datetime

<author>
    owner:
        object: <user>
        relation: ForeignKey

    name: string
    aka:
        objects: <author>
        relation: ManyToMany
    date_created: datetime
    date_modified: datetime

<collection>
    owner:
        object: <user>
        relation: ForeignKey

    name: string
    color: string
    pinned: bool
    description: string
    date_created: datetime
    date_modified: datetime

<tag>
    owner:
        object: <user>
        relation: ForeignKey

    name: string
    color: string
    description: string
    pinned: bool
    date_created: datetime
    date_modified: datetime

<topic>
    owner:
        object: <user>
        relation: ForeignKey

    name: string
    date_created: datetime
    date_modified: datetime

<medium>
    owner:
        object: <user>
        relation: ForeignKey

    name: string

<origin>
    owner:
        object: <user>
        relation: ForeignKey

    name: string
    date_created: datetime
    date_modified: datetime
```