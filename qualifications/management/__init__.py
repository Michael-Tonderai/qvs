# qualifications/management/__init__.py
#
# Present so that Django's management-command discovery treats this directory as a
# package. Django looks for INSTALLED_APPS/<app>/management/commands/*.py and finds
# nothing at all if either level is not importable.
