from __future__ import print_function
import re
import spacy
import en_core_web_sm

from pyclausie import ClausIE

nlp = en_core_web_sm.load()

re_spaces = re.compile(r'\s+')

cl = ClausIE.get_instance()


class Person(object):
    def __init__(self, name, likes=None, has=None, travels=None):
        """
        :param name: the person's name
        :type name: basestring
        :param likes: (Optional) an initial list of likes
        :type likes: list
        :param dislikes: (Optional) an initial list of likes
        :type dislikes: list
        :param has: (Optional) an initial list of things the person has
        :type has: list
        :param travels: (Optional) an initial list of the person's travels
        :type travels: list
        """
        self.name = name
        self.likes = [] if likes is None else likes
        self.has = [] if has is None else has
        self.travels = [] if travels is None else travels

    def __repr__(self):
        return self.name


class Pet(object):
    def __init__(self, pet_type, name=None):
        self.name = name
        self.type = pet_type


class Trip(object):
    def __init__(self, departs_on, departs_to=None):
        self.departs_on = departs_on
        self.departs_to = departs_to


persons = []
pets = []
trips = []


def process_data_from_input_file(file_path='./assignment_01.data'):
    with open(file_path) as infile:
        cleaned_lines = [line.strip() for line in infile if (not line.startswith(('$$$', '###', '==='))) and len(line.strip()) != 0]

    return cleaned_lines


def select_person(name):
    for person in persons:
        if person.name == name:
            return person


def add_person(name):
    person = select_person(name)

    if person is None:
        new_person = Person(name)
        persons.append(new_person)

        return new_person

    return person


def select_pet(name):
    for pet in pets:
        if pet.name == name:
            return pet


def add_pet(type, name=None):
    pet = None

    if name:
        pet = select_pet(name)

    if pet is None:
        pet = Pet(type, name)
        pets.append(pet)

    return pet


def select_trip(departs_on, departs_to):
    for trip in trips:
        if trip.departs_on == departs_on and trip.departs_to == departs_to:
            return trip


def add_trip(departs_on, departs_to=None):
    trip = None

    if departs_to:
        trip = select_trip(departs_on, departs_to)

    if trip is None:
        trip = Trip(departs_on,departs_to)
        trips.append(trip)

    return trip


def get_persons_pet(person_name):
    person = select_person(person_name)

    for thing in person.has:
        if isinstance(thing, Pet):
            return thing


def get_persons_likes(person_name, personName):
    person = select_person(person_name)

    for thing in person.likes:
        if isinstance(thing, Person) and thing.name == personName:
            return person


def get_person_travels(person_name, departs_to):
    person = select_person(person_name)

    for thing in person.travels:
        if isinstance(thing, Trip) and thing.departs_to == departs_to:
            return thing


def process_relation_triplet(triplet):
    """
    Process a relation triplet found by ClausIE and store the data
    find relations of types:
    (PERSON, likes, PERSON)
    (PERSON, has, PET)
    (PET, has_name, NAME)
    (PERSON, travels, TRIP)
    (TRIP, departs_on, DATE)
    (TRIP, departs_to, PLACE)
    :param triplet: The relation triplet from ClausIE
    :type triplet: tuple
    :return: a triplet in the formats specified above
    :rtype: tuple
    """

    sentence = triplet.subject + ' ' + triplet.predicate + ' ' + triplet.object

    doc = nlp(unicode(sentence))

    global root

    for t in doc:
        if t.pos_ == 'VERB' and t.head == t:
            root = t
        print()
        # else t.pos_ == 'NOUN'

    # also, if only one sentence
    # root = doc[:].root
    # global root

    # if root is True:
    # return True

    """
    CURRENT ASSUMPTIONS:
    - People's names are unique (i.e. there only exists one person with a certain name).
    - Pet's names are unique
    - The only pets are dogs and cats
    - Only one person can own a specific pet
    - A person can own only one pet
    """
    # Process (PERSON, likes, PERSON) relations
    if root.lemma_ == 'like' and 'does' not in triplet.predicate:
        if triplet.subject in [e.text for e in doc.ents if (e.label_ == 'PERSON' or e.text in KNOWN_NAMES)] and triplet.object in [e.text for e in doc.ents if (e.label_ == 'PERSON' or e.text in KNOWN_NAMES)]:
            s = add_person(triplet.subject)
            o = add_person(triplet.object)
            if o not in s.likes:
                s.likes.append(o)

    if root.lemma_ == 'be' and triplet.object.startswith('friends with'):
        fw_doc = nlp(unicode(triplet.object))
        if triplet.subject in [e.text for e in doc.ents if (e.label_ == 'PERSON' or e.text in KNOWN_NAMES)]:
            s = add_person(triplet.subject)

        for e in fw_doc.ents:
            if e.label_ == 'PERSON'or e.text in KNOWN_NAMES :
                o = add_person(e.text)
                if o not in s.likes:
                    s.likes.append(o)
                if s not in o.likes:
                    o.likes.append(s)

    if root.lemma_ == 'be' and 'and' in triplet.subject and triplet.object.startswith('friends'):
        fw_doc = nlp(unicode(triplet.subject))
        fw_who = [e for e in fw_doc.ents if (e.label_ == 'PERSON' or e.text in KNOWN_NAMES)][0].text
        fw_and = [e for e in fw_doc.ents if (e.label_ == 'PERSON' or e.text in KNOWN_NAMES)][1].text

        if fw_and in [e.text for e in doc.ents if (e.label_ == 'PERSON' or e.text in KNOWN_NAMES)] and fw_who in [e.text for e in doc.ents if (e.label_ == 'PERSON' or e.text in KNOWN_NAMES)]:
            s = add_person(fw_who)
            o = add_person(fw_and)
            if o not in s.likes:
                s.likes.append(o)
            if s not in o.likes:
                o.likes.append(s)

    # Process (PERSON, has, PET) Relations
    if triplet.subject.endswith('name') and ('dog' in triplet.subject or 'cat' in triplet.subject):
        obj_span = doc.char_span(sentence.find(triplet.object), len(sentence))
        name_list = list(obj_span.noun_chunks)

        if len(obj_span) == 1 and obj_span[0].pos_ == 'PROPN':
            name = triplet.object
        else:
            name = name_list[0].text

        subj_start = sentence.find(triplet.subject)
        subj_doc = doc.char_span(subj_start, subj_start + len(triplet.subject))

        s_people = [token.text for token in subj_doc if (token.ent_type_ == 'PERSON' or token.text in KNOWN_NAMES)]
        assert len(s_people) == 1
        s_person = add_person(s_people[0])

        s_pet_type = 'dog' if 'dog' in triplet.subject else 'cat'

        pet = add_pet(s_pet_type, name)

        s_person.has.append(pet)

    if root.lemma_ == 'have' and ('named' in triplet.object) and ('dog' in triplet.object or 'cat' in triplet.object):
        hd_doc = nlp(unicode(triplet.object))
        name_token = [t for t in hd_doc if t.text == 'named'][0]
        s_pet = [t for t in name_token.children if t.dep_ == 'oprd'][0]

        if [t for t in s_pet.children if t.dep_ == 'compound']:
            name = ' '.join([t.text for t in name_token.subtree if t.pos_=='PROPN'])
        else:
            name = s_pet.text

        if triplet.subject in [e.text for e in doc.ents if (e.label_ == 'PERSON' or e.text in KNOWN_NAMES)]:
            s_person = add_person(triplet.subject)

            s_pet_type = 'dog' if 'dog' in triplet.object else 'cat'
            pet = add_pet(s_pet_type, name)
            s_person.has.append(pet)

    # Process (PERSON, travels, TRIP) Relations
    if root.lemma_ in ['take', 'fly', 'leave', 'go'] and ('to' in triplet.object or 'for' in triplet.object) and len(triplet.object) > 10:
        tt_doc = nlp(unicode(triplet.object))
        trip_token = [t for t in tt_doc if (t.text == 'to' or t.text == 'for')][0]
        s_trip_to = [t for t in trip_token.children if t.dep_ == 'pobj'][0].text

        if root.children is not None:
            s_trip_on = triplet.object
        else:
            s_trip_on = ''

        for e in doc.ents:
            if e.label_ == 'PERSON' or e.text in KNOWN_NAMES:
                s_person = add_person(e.text)
                trip = add_trip(s_trip_on, s_trip_to)
                s_person.travels.append(trip)


def preprocess_question(question):
    # remove articles: a, an, the

    q_words = question.split(' ')

    # when won't this work?
    for article in ('a', 'an', 'the'):
        try:
            q_words.remove(article)
        except:
            pass
    pre_processed_ques = re.sub(re_spaces, ' ', ' '.join(q_words))
    pre_processed_ques = pre_processed_ques.replace('\'s', ' is')
    return pre_processed_ques


def has_question_word(string):
    # note: there are other question words
    for qword in ('who', 'what'):
        if qword in string.lower():
            return True

    return False


def answer_question(question_string=None):
    sents = process_data_from_input_file()

    global KNOWN_NAMES
    KNOWN_NAMES = {'Sally'}

    triples = cl.extract_triples(sents)

    for t in triples:
        r = process_relation_triplet(t)
        # print(r)

    question = question_string
    if question[-1] != '?':
        print('This is not a question... please try again')

    try:
        q_trip = cl.extract_triples([preprocess_question(question)])[0]
    except:
        q_trip = cl.extract_triples([preprocess_question('This is an invalid question')])[0]

    # Ques1: (WHO, has, PET)
    if q_trip.subject.lower() == 'who' and (q_trip.object == 'dog' or q_trip.object == 'cat'):
        answer = '{} has a {} named {}.'

        for person in persons:
            pet = get_persons_pet(person.name)
            if pet and (pet.type == q_trip.object):
                print(answer.format(person.name, 'dog', pet.name))

    # Ques2: (Who, flying/travelling/going, PLACE)
    elif q_trip.subject.lower() == 'who' and ('is' in q_trip.predicate) and q_trip.object is not None:
        answer = '{} {} {}.'
        place = q_trip.object.split()
        for person in persons:
            trip = get_person_travels(person.name, place[1])
            if trip and trip.departs_to == place[1]:
                print(answer.format(person.name,q_trip.predicate,q_trip.object,))

    # Ques3: (Does PERSON, like, PERSON)
    elif 'does' in q_trip.subject.lower() and 'like' in q_trip.predicate and q_trip.object is not None:
        name = q_trip.subject.split()
        person = get_persons_likes(name[1], q_trip.object)
        if person and person.name != q_trip.object:
            print('Yes, ' + name[1] + ' likes ' + q_trip.object + '.')
        else:
            print('No, ' + name[1] + ' does not like ' + q_trip.object + '.')

    # Ques4: (When, PERSON, flying/traveling/going, PLACE)
    elif 'when' in q_trip.object.lower() and q_trip.subject is not None:
        answer = '{} {} {}.'
        name = q_trip.subject
        place = q_trip.object.split()
        place1=place[1]
        trip = get_person_travels(name, place1)
        if trip and trip.departs_to == place1:
            print(answer.format(q_trip.subject,q_trip.predicate,trip.departs_on))

    # Ques5: (WHO, likes, PERSON)
    elif q_trip.subject.lower() == 'who' and 'likes' in q_trip.predicate and q_trip.object is not None:
        answer = '{} likes {}.'

        for person in persons:
            person = get_persons_likes(person.name, q_trip.object)
            if person and person.name != q_trip.object:
                print(answer.format(person.name, q_trip.object))

    # Ques6: (Who, does PERSON, like)
    elif q_trip.subject is not None and 'like' in q_trip.predicate.lower() and q_trip.object.lower() == 'who':
        answer = '{} likes {}.'
        person_name = select_person(q_trip.subject)
        for person in person_name.likes:
            print(answer.format(person_name.name, person.name))

    # Ques7: (What's PERSON's, PET, name)
    elif 'what' in [q.text.lower() for q in nlp(unicode(preprocess_question(question)))] and 'name' in [q.text.lower() for q in nlp(unicode(preprocess_question(question)))] and 'PERSON' in [token.ent_type_ for token in nlp(unicode(preprocess_question(question)))]:
        s_person = select_person([token.text for token in nlp(unicode(preprocess_question(question))) if token.ent_type_ == 'PERSON'][0])
        pet = get_persons_pet(s_person.name)
        if pet and (pet.type == 'cat' or pet.type == 'dog'):
            print(s_person.name + '\'s',pet.type + '\'s name is',pet.name)

    else:
        print("I don't know")
