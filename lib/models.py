#!/usr/bin/env python3

import itertools
import json
import os

import yaml


__all__ = [
    'GENERATION_NAMES',
    'MemberList',
    'SNH48',
    'TEAM_IDS',
    'TIERS',
    'TIER_NAMES',
    'TIER_MEMBERS',
    'TeamS2',
    'TeamN2',
    'TeamH2',
    'TeamX',
    'TeamX2',
]

HERE = os.path.dirname(os.path.realpath(__file__))
ROOT = os.path.dirname(HERE)
DATA_DIR = os.path.join(ROOT, 'data')
MEMBERS_YML = os.path.join(DATA_DIR, 'members.yml')
PERFORMANCES_JSON = os.path.join(DATA_DIR, 'performances.json')

TEAM_IDS = ['s2', 'n2', 'h2', 'x', 'x2']
GENERATION_NAMES = {
    1: '一期生',
    2: '二期生',
    3: '三期生',
    4: '四期生',
    5: '五期生',
    6: '六期生',
    7: '七期生',
    8: '八期生',
}
TIERS = ['3-1', '3-2', '3-3', '4-1', '4-2', '4-3', '4-4']
TIER_NAMES = {
    # 3rd Election
    '3-1': '三选高飞组',
    '3-2': '三选梦想组',
    '3-3': '三选起飞组',
    # 4th Election
    '4-1': '四选星光组',
    '4-2': '四选高飞组',
    '4-3': '四选梦想组',
    '4-4': '四选奔跑组',
}
TIER_MEMBERS = {
    # 3rd Election
    '3-1': [
        ('鞠婧祎', 1),
        ('李艺彤', 2),
        ('黄婷婷', 3),
        ('曾艳芬', 4),
        ('冯薪朵', 5),
        ('莫寒', 6),
        ('陆婷', 7),
        ('张语格', 8),
        ('赵粤', 9),
        ('邱欣怡', 10),
        ('许佳琪', 11),
        ('戴萌', 12),
        ('林思意', 13),
        ('万丽娜', 14),
        ('刘炅然', 15),
        ('张丹三', 16),
    ],
    '3-2': [
        ('龚诗淇', 17),
        ('宋昕冉', 18),
        ('许杨玉琢', 19),
        ('李宇琪', 20),
        ('孙珍妮', 21),
        ('费沁源', 22),
        ('吴哲晗', 23),
        ('杨韫玉', 24),
        ('孔肖吟', 25),
        ('易嘉爱', 26),
        ('钱蓓婷', 28),
        ('袁雨桢', 29),
        ('谢妮', 30),
        ('洪珮雲', 31),
        ('姜杉', 32),
    ],
    '3-3': [
        ('张怡', 33),
        ('杨惠婷', 34),
        ('徐子轩', 35),
        ('严佼君', 36),
        ('刘佩鑫', 37),
        ('陈思', 38),
        ('杨冰怡', 39),
        # ('王璐', 41),
        # ('陈怡馨', 42),
        ('邵雪聪', 44),
        ('王晓佳', 45),
        ('於佳怡', 46),
        ('陈观慧', 47),
    ],
    # 4th Election
    '4-1': [
        ('鞠婧祎', 1),
        ('李艺彤', 2),
        ('黄婷婷', 3),
        ('冯薪朵', 4),
        ('陆婷', 5),
        ('曾艳芬', 6),
        ('赵粤', 7),
        ('莫寒', 8),
        ('张语格', 9),
        ('许佳琪', 10),
        ('戴萌', 11),
        ('孔肖吟', 12),
        ('林思意', 14),
        ('吴哲晗', 15),
        ('李宇琪', 16),
    ],
    '4-2': [
        ('万丽娜', 17),
        ('孙芮', 18),
        ('姜杉', 19),
        ('张雨鑫', 20),
        ('孙珍妮', 22),
        ('刘炅然', 24),
        ('杨冰怡', 25),
        ('钱蓓婷', 26),
        ('许杨玉琢', 27),
        ('於佳怡', 28),
        ('宋昕冉', 29),
        ('严佼君', 30),
        ('张怡', 31),
    ],
    '4-3': [
        ('袁航', 33),
        ('吕一', 36),
        ('李钊', 38),
        ('易嘉爱', 39),
        ('费沁源', 40),
        ('汪束', 41),
        ('徐子轩', 42),
        ('王晓佳', 43),
        ('蒋芸', 44),
        ('冯晓菲', 47),
        ('杨惠婷', 48),
    ],
    '4-4': [
        ('洪珮雲', 49),
        ('郝婉晴', 51),
        ('杨韫玉', 52),
        ('张丹三', 53),
        ('陈琳', 54),
        ('江真仪', 55),
        ('袁一琦', 56),
        ('何晓玉', 59),
        ('谢妮', 60),
        ('陈观慧', 61),
        ('刘增艳', 63),
        ('袁雨桢', 64),
        ('沈梦瑶', 65),
    ],
}


class Member(object):

    def __init__(self, name, affiliation, generation):
        self._name = name
        self._affiliation = affiliation
        self._generation = generation

    def __str__(self):
        return f'{Team.printable(self._affiliation)} - {self._name}'

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        return self._name == other._name and self._generation == other._generation

    def __hash__(self):
        return hash(repr(self))

    @property
    def name(self):
        return self._name

    @property
    def affiliation(self):
        return SNH48.getteam(self._affiliation)

    @property
    def generation(self):
        return self._generation


class MemberList(object):

    def __init__(self, members=None):
        if members is not None:
            try:
                self._members = set(map(SNH48.get, members))
            except NameError:
                # SNH48 is not defined during the instantiation of _SNH48 itself.
                self._members = set(members)
        else:
            self._members = set()
        self._names = set(member.name for member in self._members)

    def __str__(self):
        return ', '.join(member.name for member in self)

    def __repr__(self):
        reprs = [f"'{repr(member)}'" for member in self]
        return '[' + ', '.join(reprs) + ']'

    def __iter__(self):
        return (member for member in sorted(self._members, key=SNH48.index))

    def __contains__(self, member):
        return SNH48.get(member).name in self._names

    @property
    def members(self):
        return iter(self)

    def add(self, member):
        member = SNH48.get(member)
        if member not in self:
            self._members.add(member)
            self._names.add(member.name)

    def sorted(self):
        return list(self)


class Performance(object):

    def __init__(self, date, title, affiliation, stage, performers):
        self._date = date
        self._title = title
        self._affiliation = affiliation
        self._stage = stage
        self._performers = MemberList(performers)

    def __str__(self):
        return self.title

    def __repr__(self):
        performers_repr = repr(self._performers)
        return f"{{'title': '{self._title}', 'affiliation': '{self._affiliation}', 'performers': {performers_repr}}}"

    def __contains__(self, member):
        return member in self._performers

    @property
    def date(self):
        return self._date

    @property
    def title(self):
        return self._title

    @property
    def affiliation(self):
        try:
            return SNH48.getteam(self._affiliation)
        except LookupError:
            return None

    @property
    def stage(self):
        return self._stage

    @property
    def performers(self):
        return iter(self._performers)


# A shared instance is created for each unique team identifier. For each
# unique team identifier, the shared instance is only initialized once,
# so team members cannot be updated through re-initialization.
class Team():
    __shared_states = {}

    def __init__(self, team_id, members=None, aids=None):
        if team_id not in TEAM_IDS:
            raise LookupError(f'{team_id} is not a recognized team identifier')
        if team_id not in self.__shared_states:
            self.__shared_states[team_id] = {}
        self.__dict__ = self.__shared_states[team_id]

        if hasattr(self, '_initialized'):
            return

        self._team_id = team_id
        self._members = MemberList(members)
        self._aids = MemberList(aids)
        self.performances = []

        self._initialized = True

    def __str__(self):
        return f'Team {Team.printable(self._team_id)}'

    def __repr__(self):
        members_repr = repr(self._members)
        aids_repr = repr(self._aids)
        return f"{{'team_id': '{self._team_id}', 'members': {members_repr}, 'aids': {aids_repr}}}"

    def __eq__(self, other):
        return self._team_id == other._team_id

    def __hash__(self):
        return hash(self._team_id)

    def __contains__(self, member):
        return member in self._members

    @property
    def team_id(self):
        return self._team_id

    @property
    def members(self):
        """An iterator for regular members of the team."""
        return iter(self._members)

    @property
    def aids(self):
        """An iterator for aids to the team."""
        return iter(self._aids)

    @property
    def all(self):
        """An iterator joining members and aids."""
        return itertools.chain(self.members, self.aids)

    def add_member(self, member):
        self._members.add(member)

    def add_aid(self, member):
        self._aids.add(member)

    @staticmethod
    def printable(team_id):
        if team_id == 's2':
            return 'SⅡ'
        elif team_id == 'n2':
            return 'NⅡ'
        elif team_id == 'h2':
            return 'HⅡ'
        elif team_id == 'x':
            return 'X'
        elif team_id == 'x2':
            return 'XⅡ'
        else:
            raise LookupError(f'{team_id} is not a recognized team identifier')


# Similar to Team, but much more lightweight.
class Generation(MemberList):
    __shared_states = {}

    def __init__(self, generation, members=None):
        if generation not in GENERATION_NAMES:
            raise LookupError(f'{generation} is not a recognized generation')
        if generation not in self.__shared_states:
            self.__shared_states[generation] = {}
        self.__dict__ = self.__shared_states[generation]

        if hasattr(self, '_initialized'):
            return

        self._generation = generation
        super().__init__(members)

        self._initialized = True

    def __str__(self):
        return GENERATION_NAMES[self._generation]

    def __repr__(self):
        members_repr = super().__repr__()
        return f"{{'{str(self)}': {members_repr}}}"

    @property
    def generation(self):
        return self._generation


# A plain list of members with a tier property, custom string representations,
# and the ability to assign arbitrary attributes.
class Tier(list, object):
    __shared_states = {}

    def __init__(self, tier, members=None):
        if tier not in TIER_NAMES:
            raise LookupError(f'{tier} is not a recognized tier')
        if tier not in self.__shared_states:
            self.__shared_states[tier] = {}
        self.__dict__ = self.__shared_states[tier]

        if hasattr(self, '_initialized'):
            return

        self._tier = tier
        list.__init__(self, members)

        self._initialized = True

    def __str__(self):
        return TIER_NAMES[self._tier]

    def __repr__(self):
        members_repr = super().__repr__()
        return f"{{'{str(self)}': {members_repr}}}"

    @property
    def tier(self):
        return self._tier


# Singleton class for the whole group.
class _SNH48(object):
    __shared_state = {}

    def __init__(self):
        self.__dict__ = self.__shared_state

        if hasattr(self, '_initialized'):
            return

        self._members = []
        self._name_obj_map = {}
        self._name_index_map = {}
        with open(MEMBERS_YML) as fp:
            members = yaml.load(fp)
            for index, member in enumerate(members):
                name = member['name']
                affiliation = member['affiliation']
                generation = member['generation']
                obj = Member(name, affiliation, generation)
                self._members.append(obj)
                self._name_index_map[name] = index
                self._name_obj_map[name] = obj

        self.teams = {}
        for team_id in TEAM_IDS:
            team_members = [member for member in self._members if member._affiliation == team_id]
            team = Team(team_id, team_members)
            self.teams[team_id] = team
            attrname = f'Team{team_id.upper()}'
            setattr(self, attrname, team)

        self.generations = {}
        for generation in range(1, 9):
            self.generations[generation] = Generation(
                generation,
                [member for member in self._members if member.generation == generation]
            )

        self.tiers = {}
        for tier in TIERS:
            members = []
            for name, rank in TIER_MEMBERS[tier]:
                member = self._name_obj_map[name]
                members.append(member)
            self.tiers[tier] = Tier(tier, members)

        self._initialized = True

        self.performances = []
        self.joint_performances = []

    def __str__(self):
        return 'SNH48'

    def __repr__(self):
        team_reprs = []
        for attrname in 'TeamS2', 'TeamN2', 'TeamH2', 'TeamX', 'TeamX2':
            team_repr = repr(getattr(self, attrname))
            team_reprs.append(f"'{attrname}': {team_repr}")
        return '{' + ', '.join(team_reprs) + '}'

    def __eq__(self, other):
        return True

    def __iter__(self):
        return (member for member in self._members)

    @property
    def members(self):
        return iter(self)

    def get(self, member):
        """Get a member by name.

        If the argument is a str, returns a Member object if there is a
        member with that name; otherwise, raises a LookupError. If the
        argument is already a Member object, do nothing (this is so that
        we can accept either str or Member in other places and call
        SNH48.get unconditionally).

        """
        if isinstance(member, Member):
            return member
        elif isinstance(member, str):
            if member in self._name_obj_map:
                return self._name_obj_map[member]
            else:
                raise LookupError(f'{member} not found')
        else:
            raise TypeError(f'expecting str or Member, got {type(member).__name__}')

    def getteam(self, team_id):
        if team_id in self.teams:
            return self.teams[team_id]
        else:
            raise LookupError(f'{team_id} is not a recognized team identifier')

    def index(self, member):
        '''Index of a member used for sorting.'''
        return self._name_index_map[self.get(member).name]


def load_performances():
    with open(PERFORMANCES_JSON) as fp:
        for performance in json.load(fp):
            obj = Performance(**performance)
            affiliation = performance['affiliation']
            SNH48.performances.append(obj)
            if affiliation in TEAM_IDS:
                team = SNH48.teams[affiliation]
                team.performances.append(obj)
                for member in obj.performers:
                    if member not in team:
                        # We're actually counting cameo appearances as
                        # aids, which sure is sloppy... But it doesn't
                        # affect the outcome much, so whatever.
                        #
                        # If we really want to be pedantic, we could
                        # simply hard-code all the external aids; there
                        # aren't that many to begin with.
                        team.add_aid(member)
            else:
                SNH48.joint_performances.append(obj)


SNH48 = _SNH48()
TeamS2 = SNH48.TeamS2
TeamN2 = SNH48.TeamN2
TeamH2 = SNH48.TeamH2
TeamX = SNH48.TeamX
TeamX2 = SNH48.TeamX2
load_performances()
