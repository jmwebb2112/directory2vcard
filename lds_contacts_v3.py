#!/usr/bin/env python3
import argparse
import re
import sys


DEFAULT_AREA_CODE = '801'

NAME_REGEX = re.compile(r'[^A-Za-z,\-\' ]')



class EmptyStrException(Exception):
    """
    Validation exception for empty strings
    """


class InvalidPhoneException(Exception):
    """
    Validation exception for invalid phone
    """


class PhoneRec():
    def __init__(self, fname, lname, phone, email, group):
        self.fname = fname
        self.lname = lname
        self.phone = phone
        self._email = email
        self._group = group

    def __repr__(self):
        items = [v for v in self.__dict__.values()]
        return '{}({})'.format(self.__class__.__name__, ','.join(items))

    @property
    def fname(self):
        return self._fname

    @fname.setter
    def fname(self, value):
        if not(value.strip()):
            raise EmptyStrException('First Name cannot be empty')
        self._fname = value

    @property
    def lname(self):
        return self._lname

    @lname.setter
    def lname(self, value):
        if not(value.strip()):
            raise EmptyStrException('Last Name cannot be empty')
        self._lname = value

    @property
    def phone(self):
        return self._phone

    @phone.setter
    def phone(self, value):
        pn = self.format_phone(value)
        if not pn:
            raise InvalidPhoneException('Invalid phone # {}'.format(value))
        self._phone = pn

    @property
    def email(self):
        return self._email

    @property
    def group(self):
        return self._group

    def format_phone(self, instr, def_ac=DEFAULT_AREA_CODE):
        tempphn = '1' + def_ac + '5555555'
        tlen = len(tempphn)
        cleanphone = ''.join(i for i in instr if i.isdigit())
        if len(cleanphone) < 7 or len(cleanphone) > 11:
            return ''
        return tempphn[0:tlen - len(cleanphone)] + cleanphone


def build_rec(first, last, phone, email, group):
    try:
        fr = PhoneRec(first, last, phone, email, group)
    except (EmptyStrException, InvalidPhoneException) as e:
        fr = None
    return fr


def split_name(name_str):
    if name_str:
        names = [x.strip() for x in name_str.split(',')]
        if len(names) < 2:
            names.append('')
        return (names[1], names[0])
    return ('', '')

def is_name(fld):
    flds = fld.split(',')
    m = NAME_REGEX.search(fld)
    return len(flds) == 2 and not m

def is_phone(fld):
    digs = re.sub('\D', '', fld)
    return len(digs) >= 7 and len(digs) <= 11

def is_email(fld):
    return '@' in fld and '.' in fld and ' ' not in fld


def process_row(row, group):
    row_rec = row.split('|')
    frec = None
    recs = []
    # Full row format is Last, First|Ind Phone|Ind Email|Home Phone|Home Email
    row_vals = {'Name': '', 'Phone': '', 'Email': ''}
    for fld in row_rec:
        if not fld:
            continue
        if not row_vals['Name'] and is_name(fld):
            row_vals['Name'] = fld.strip()
        elif not row_vals['Phone'] and is_phone(fld):
            row_vals['Phone'] = fld.strip()
        elif not row_vals['Email'] and is_email(fld):
            row_vals['Email'] = fld.strip()

    if row_vals['Name'] and row_vals['Phone']:
        frec = build_rec(
            *split_name(row_vals['Name']),
            row_vals['Phone'],
            row_vals['Email'],
            group
        )
        recs.append(frec)
    if not recs:
        print('Skipping raw record: ', row)
    return recs


def write_vcf_record(output, prec):
    output.write("BEGIN:VCARD\n")
    output.write("VERSION:3.0\n")
    output.write("N:{0};{1};;;\n".format(prec.lname, prec.fname))
    output.write("FN: {0} {1}\n".format(prec.fname, prec.lname))
    output.write("TEL;TYPE=HOME:{0}\n".format(prec.phone))

    if prec.email:
        output.write("EMAIL:{0}\n".format(prec.email))

    output.write("item1.ADR;TYPE=OTHER;TYPE=pref:;;{0};;;;;\n"
                 .format(prec.group))
    output.write("END:VCARD\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Utility to parse ward directory csv dump from lds.org",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.set_defaults(
        areacode='801',
        infile=None,
        outfile=None,
        group=None,
    )
    parser.add_argument(
        '-i', '--infile', dest="infile", required=True,
        help='CSV input file path'
    )
    parser.add_argument(
        '-o', '--outfile', dest='outfile', required=True,
        help='Path to VCARD output'
    )
    parser.add_argument(
        '-a', '--areacode', dest='areacode',
        help='Areacode to use in phone numbers, default=801'
    )
    parser.add_argument(
        '-g', '--group', dest='group',
        help='Group name to assign in VCARD'
    )
    args = parser.parse_args()
    DEFAULT_AREA_CODE = args.areacode

    outfile = open(args.outfile, 'w')
    group_tag = args.group if args.group else ''

    with open(args.infile, 'r') as csvfile:
        for row in csvfile:
            for rec in process_row(row, group_tag):
                print("RAW: ", row)
                print("Record: ", rec)
                print('-----------------')
                write_vcf_record(outfile, rec)
