from subprocess import call

from django.conf import settings
from django.core.management.base import BaseCommand

from exercises.models import KhanExerciseTreeNode

POST_LOAD_JS = """
    $(document).ready(function() {
        $('header, footer, #answer_area_wrap, #warning-bar, #extras, .exercise-badge, .exercises-header, .exercises-stack').hide();
        $('*').css('border', 'none');
        $('*').css('box-shadow', 'none');
        $('body').css('min-width', '0px');
        $('#page-container').css('min-width', '0px');
        $('#page-container').css('max-width', 'none');
        $('article').css('padding', '0 0 0 0');
        $('article').css('margin', '0 0 0 0');
        $('.exercises-card').css('width', 'auto');
        $('#outer-wrapper').css('height', 'auto');
        $('*').css('background', 'transparent');
    });
"""

def _generate_screenshots():
    exercises = KhanExerciseTreeNode.objects.filter(live=True).exclude(url=None)
    urls = [e.url for e in exercises if '#' not in e.url]

    # This should work fine, but there's a little issue with the webkit2png
    # with large lists of urls.  So we'll call the process instead, on 5 urls
    # at a time.
    #options = {
    #    'dir': settings.KHAN_EXERCISE_SCREENSHOT_DIR,
    #    'js': POST_LOAD_JS,
    #    'transparent': True,
    #    'fullsize': True,
    #    'delay': 2
    #}
    #from webkit2png import create_pngs
    #create_pngs(*urls, **options)

    for e in exercises:
      if '#' in e.url:
        continue

      file_name = e.parent.display_name + "_" + e.display_name
      file_name.replace(' ', '_')
      file_name = file_name.replace(' ', '_')
      options = [
          '--dir', settings.KHAN_EXERCISE_SCREENSHOT_DIR,
          '--js', POST_LOAD_JS,
          '--transparent',
          '--fullsize',
          '--delay', '2',
          '--filename', file_name
      ]
      args = ['webkit2png'] + [e.url] + options
      call(args)

class Command(BaseCommand):
    help = 'Generates PNG screenshots of each live exercise in the database.'

    def handle(self, *args, **options):
        _generate_screenshots()
