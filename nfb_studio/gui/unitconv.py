"""Converts units in inches to units in pixels using logical dpi of the application."""
from typing import Union
from Qt.QtCore import QPoint, QPointF, QSize, QSizeF, QRect, QRectF
from Qt.QtWidgets import QApplication, QWidget


def dpi():
    """Return this application's logical dpi"""
    # Check if the application has been created. If the application has not been created, dpi cannot be measured.
    if QApplication.instance() is None:
        raise RuntimeError("dpi(): Must construct a QApplication before measuring dpi")

    return QWidget().logicalDpiX()


def inches_to_pixels(value: Union[int, float, QPoint, QPointF, QSize, QSizeF, QRect, QRectF]):
    """Convert a value in inches to a value in pixels.
    Supports values: plain numbers, QPoint, QPointF, QSize, QSizeF, QRect, QRectF.
    """
    if type(value) is QRect:
        return QRect(
            value.topLeft() * dpi(),
            value.bottomRight() * dpi()
        )

    if type(value) is QRectF:
        return QRectF(
            value.topLeft() * dpi(),
            value.bottomRight() * dpi()
        )

    return value * dpi()


def pixels_to_inches(value):
    """Convert a value in pixels to a value in inches."""
    if type(value) is QRect:
        return QRect(
            value.topLeft() / dpi(),
            value.bottomRight() / dpi()
        )

    if type(value) is QRectF:
        return QRectF(
            value.topLeft() / dpi(),
            value.bottomRight() / dpi()
        )

    return value / dpi()
