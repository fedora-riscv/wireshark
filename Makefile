# Makefile for source rpm: wireshark
# $Id$
NAME := wireshark
SPECFILE = $(firstword $(wildcard *.spec))

include ../common/Makefile.common
