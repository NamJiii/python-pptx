# encoding: utf-8

"""
Objects related to mouse click and hover actions on a shape or text.
"""

from __future__ import (
    absolute_import, division, print_function, unicode_literals
)

from .enum.action import PP_ACTION
from .shapes import Subshape
from .util import lazyproperty


class ActionSetting(Subshape):
    """
    Properties that specify how a shape or text run reacts to mouse actions
    during a slide show.
    """
    # Subshape superclass provides access to the Slide Part, which is needed
    # to access relationships.
    def __init__(self, xPr, parent, hover=False):
        super(ActionSetting, self).__init__(parent)
        # xPr is either a cNvPr or rPr element
        self._element = xPr
        # _hover determines use of `a:hlinkClick` or `a:hlinkHover`
        self._hover = hover

    @property
    def action(self):
        """
        A member of the :ref:`PpActionType` enumeration, such as
        `PP_ACTION.HYPERLINK`, indicating the type of action that will result
        when the specified shape or text is clicked or the mouse pointer is
        positioned over the shape during a slide show.
        """
        hlink = self._hlink

        if hlink is None:
            return PP_ACTION.NONE

        action_verb = hlink.action_verb

        if action_verb == 'hlinkshowjump':
            relative_target = hlink.action_fields['jump']
            return {
                'firstslide':      PP_ACTION.FIRST_SLIDE,
                'lastslide':       PP_ACTION.LAST_SLIDE,
                'lastslideviewed': PP_ACTION.LAST_SLIDE_VIEWED,
                'nextslide':       PP_ACTION.NEXT_SLIDE,
                'previousslide':   PP_ACTION.PREVIOUS_SLIDE,
                'endshow':         PP_ACTION.END_SHOW,
            }[relative_target]

        return {
            None:           PP_ACTION.HYPERLINK,
            'hlinksldjump': PP_ACTION.NAMED_SLIDE,
            'hlinkpres':    PP_ACTION.PLAY,
            'hlinkfile':    PP_ACTION.OPEN_FILE,
            'customshow':   PP_ACTION.NAMED_SLIDE_SHOW,
            'ole':          PP_ACTION.OLE_VERB,
            'macro':        PP_ACTION.RUN_MACRO,
            'program':      PP_ACTION.RUN_PROGRAM,
        }[action_verb]

    @property
    def target_slide(self):
        """
        A reference to the slide in this presentation that is the target of
        the slide jump action in this shape. Slide jump actions include
        `PP_ACTION.FIRST_SLIDE`, `LAST_SLIDE`, `NEXT_SLIDE`,
        `PREVIOUS_SLIDE`, and `NAMED_SLIDE`. Returns |None| for all other
        actions. In particular, the `LAST_SLIDE_VIEWED` action and the `PLAY`
        (start other presentation) actions are not supported.
        """
        slide_jump_actions = (
            PP_ACTION.FIRST_SLIDE,
            PP_ACTION.LAST_SLIDE,
            PP_ACTION.NEXT_SLIDE,
            PP_ACTION.PREVIOUS_SLIDE,
            PP_ACTION.NAMED_SLIDE,
        )

        if self.action not in slide_jump_actions:
            return None

        if self.action == PP_ACTION.FIRST_SLIDE:
            return self._slides[0]
        elif self.action == PP_ACTION.LAST_SLIDE:
            return self._slides[-1]
        elif self.action == PP_ACTION.NEXT_SLIDE:
            next_slide_idx = self._slide_index + 1
            if next_slide_idx >= len(self._slides):
                raise ValueError('no next slide')
            return self._slides[next_slide_idx]
        elif self.action == PP_ACTION.PREVIOUS_SLIDE:
            prev_slide_idx = self._slide_index - 1
            if prev_slide_idx < 0:
                raise ValueError('no previous slide')
            return self._slides[prev_slide_idx]
        elif self.action == PP_ACTION.NAMED_SLIDE:
            rId = self._hlink.rId
            return self._slide.rels.related_parts[rId]

    @property
    def _hlink(self):
        """
        Reference to the `a:hlinkClick` or `h:hlinkHover` element for this
        click action. Returns |None| if the element is not present.
        """
        if self._hover:
            return self._element.hlinkHover
        return self._element.hlinkClick

    @lazyproperty
    def _slide(self):
        """
        Reference to the slide containing the shape having this click action.
        """
        return self.part

    @lazyproperty
    def _slide_index(self):
        """
        Position in the slide collection of the slide containing the shape
        having this click action.
        """
        raise NotImplementedError

    @lazyproperty
    def _slides(self):
        """
        Reference to the slide collection for this presentation.
        """
        return self.part.package.presentation.slides