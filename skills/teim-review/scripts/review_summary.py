#!/usr/bin/env python3
# Copyright 2026 Sean Mooney
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

"""Derive assessment text from retained inline and HTML-only findings."""

from typing import Any


def finding_assessment(report: dict[str, Any]) -> dict[str, str]:
    """Assess all retained findings without implying merge approval."""
    inline = report.get('statistics', {})
    html = report.get('statistics_html_only', {})
    counts = {
        severity: inline.get(severity, 0) + html.get(severity, 0)
        for severity in ('critical', 'high', 'warnings', 'suggestions')
    }
    if counts['critical']:
        assessment = 'Blocked'
        focus = 'Address critical review findings before merge'
    elif counts['high']:
        assessment = 'Needs work'
        focus = 'Address high severity review findings before merge'
    elif counts['warnings']:
        assessment = 'Ready with minor fixes'
        focus = 'Review the retained warnings, including HTML-only findings'
    elif counts['suggestions']:
        assessment = 'Ready with minor fixes'
        focus = 'Consider the retained suggestions before merge'
    elif (report.get('patch_level_observations')
          or report.get('out_of_patch_observations')):
        assessment = 'Ready with minor fixes'
        focus = 'Review the observations that have no inline comment'
    else:
        assessment = 'No retained findings'
        focus = 'No reportable findings remain after publication filtering'
    return {'assessment': assessment, 'priority_focus': focus}
