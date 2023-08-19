import os

from ..pages.utils import render_head, render_footer
from flask import Flask, render_template, request, session, redirect, url_for

def test_page():
    page = render_head("test")
    page += render_template('test.jinja2')

    if request.method == 'GET':
        values = request.values
        for keys, values in values.items():
            print(keys, values)

    return page

