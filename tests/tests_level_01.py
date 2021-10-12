import unittest
import hedy
import sys
import io
from contextlib import contextmanager
import textwrap
import inspect

class HedyTester(unittest.TestCase):
  level=None

  @contextmanager
  def captured_output(self):
    new_out, new_err = io.StringIO(), io.StringIO()
    old_out, old_err = sys.stdout, sys.stderr
    try:
      sys.stdout, sys.stderr = new_out, new_err
      yield sys.stdout, sys.stderr
    finally:
      sys.stdout, sys.stderr = old_out, old_err

  def run_code(self, parse_result):
    code = "import random\n" + parse_result.code
    with self.captured_output() as (out, err):
      exec(code)
    return out.getvalue().strip()

  def test_name(self):
    return inspect.stack()[1][3]

  def is_not_turtle(self):
    return (lambda x: not x.has_turtle)

  def multi_level_tester(self, test_name, code, max_level, expected=None, exception=None, extra_check_function=None):
    # TODO: test_name could be stored in __init__ of test method
    #  if we created our own method (not sure it that is worth it?)

    # used to test the same code snippet over multiple levels
    # Use exception to check for an exception

    # Or use expect to check for an expected Python program
    # In the second case, you can also pass an extra function to check
    for level in range(self.level, max_level + 1):
      if exception is not None:
        with self.assertRaises(exception) as context:
          result = hedy.transpile(code, level)
      if expected is not None:
        result = hedy.transpile(code, level)
        self.assertEqual(expected, result.code)

      if extra_check_function is not None:
        self.assertTrue(extra_check_function(result))

      print(f'{test_name} passed for level {level}')

class TestsLevel1(HedyTester):
  level = 1

  def test_transpile_other(self):
    with self.assertRaises(hedy.InvalidCommandException) as context:
      result = hedy.transpile("abc felienne 123", self.level)
    self.assertEqual('Invalid', context.exception.error_code)

  def test_print_without_argument_upto_22(self):
    self.multi_level_tester(
      max_level=22,
      code="print",
      exception=hedy.IncompleteCommandException,
      test_name=self.test_name()
    )

  def test_transpile_incomplete_on_line_2(self):
    with self.assertRaises(hedy.IncompleteCommandException) as context:
      result = hedy.transpile("print lalalala\nprint", self.level)
    self.assertEqual('Incomplete', context.exception.error_code)
    self.assertEqual('print', str(context.exception.arguments['incomplete_command']))

  def test_transpile_incomplete_with_multiple_lines(self):
    with self.assertRaises(hedy.IncompleteCommandException) as context:
      result = hedy.transpile("print hallo allemaal\nprint", self.level)
    self.assertEqual('Incomplete', context.exception.error_code)

  # def test_transpile_other_2(self):
  #   with self.assertRaises(Exception) as context:
  #     result = hedy.transpile("abc felienne 123", self.level)
  #   self.assertEqual(str(context.exception), 'Invalid')
  #   self.assertEqual(str(context.exception.arguments),
  #                    "{'invalid_command': 'abc', 'level': 1, 'guessed_command': 'ask'}")

  def test_transpile_incomplete_not_a_keyword(self):
    with self.assertRaises(hedy.InvalidCommandException) as context:
      result = hedy.transpile("groen", self.level)
    self.assertEqual('Invalid', context.exception.error_code)

  def test_transpile_print(self):
    result = hedy.transpile("print Hallo welkom bij Hedy!", self.level)
    expected = "print('Hallo welkom bij Hedy!')"
    self.assertEqual(expected, result.code)
    self.assertEqual(False, result.has_turtle)
    self.assertEqual('Hallo welkom bij Hedy!', self.run_code(result))

  def test_print_has_no_turtle(self):
    result = hedy.transpile_inner("print koekoek", self.level)
    expected = False
    self.assertEqual(expected, result.has_turtle)

  def test_one_forward_has_turtle(self):
    result = hedy.transpile_inner("forward 50", self.level)
    expected = True
    self.assertEqual(expected, result.has_turtle)

  def test_transpile_one_forward(self):
    result = hedy.transpile("forward 50", self.level)
    expected = textwrap.dedent("""\
    t.forward(50)
    time.sleep(0.1)""")
    self.assertEqual(expected, result.code)

  def test_transpile_turn_no_args(self):
    result = hedy.transpile("turn", self.level)
    expected = textwrap.dedent("""\
    t.right(90)""")
    self.assertEqual(expected, result.code)
    self.assertEqual(True, result.has_turtle)

  def test_transpile_one_turn_right(self):
    result = hedy.transpile("turn right", self.level)
    expected = textwrap.dedent("""\
    t.right(90)""")
    self.assertEqual(expected, result.code)
    self.assertEqual(True, result.has_turtle)

  def test_transpile_one_turn_with_var(self):
    result = hedy.transpile("turn koekoek", self.level)
    expected = textwrap.dedent("""\
    t.right(90)""")
    self.assertEqual(expected, result.code)
    self.assertEqual(True, result.has_turtle)

  def test_transpile_one_turn_left(self):
    result = hedy.transpile("turn left", self.level)
    expected = textwrap.dedent("""\
    t.left(90)""")
    self.assertEqual(expected, result.code)
    self.assertEqual(True, result.has_turtle)

  def test_transpile_multiple_forward_without_arguments(self):
    result = hedy.transpile("forward\nforward", self.level)
    expected = textwrap.dedent("""\
    t.forward(50)
    time.sleep(0.1)
    t.forward(50)
    time.sleep(0.1)""")
    self.assertEqual(expected, result.code)
    self.assertEqual(True, result.has_turtle)

  def test_transpile_turtle_combi(self):
    result = hedy.transpile("forward 50\nturn\nforward 100", self.level)
    expected = textwrap.dedent("""\
    t.forward(50)
    time.sleep(0.1)
    t.right(90)
    t.forward(100)
    time.sleep(0.1)""")
    self.assertEqual(expected, result.code)
    self.assertEqual(True, result.has_turtle)


  def test_transpile_ask_Spanish(self):
    result = hedy.transpile("ask ask Cuál es tu color favorito?", self.level)
    expected = "answer = input('ask Cuál es tu color favorito?')"
    self.assertEqual(expected, result.code)
    self.assertEqual(False, result.has_turtle)

  def test_lines_may_end_in_spaces(self):
    result = hedy.transpile("print Hallo welkom bij Hedy! ", self.level)
    expected = "print('Hallo welkom bij Hedy! ')"
    self.assertEqual(expected, result.code)
    self.assertEqual(False, result.has_turtle)
    self.assertEqual('Hallo welkom bij Hedy!', self.run_code(result))

  def test_lines_may_not_start_with_spaces(self):
    with self.assertRaises(hedy.InvalidSpaceException) as context:
      result = hedy.transpile(" print Hallo welkom bij Hedy! ", self.level)
    self.assertEqual('Invalid Space', context.exception.error_code)

  def test_print_with_comma(self):
    result = hedy.transpile("print iedereen zegt tegen hem: NERD, omdat hij de slimste van de klas is.", self.level)

    expected = "print('iedereen zegt tegen hem: NERD, omdat hij de slimste van de klas is.')"
    self.assertEqual(expected, result.code)
    self.assertEqual(False, result.has_turtle)

  def test_word_plus_period(self):
    with self.assertRaises(hedy.InvalidCommandException) as context:
      result = hedy.transpile("word.", self.level)
    self.assertEqual('Invalid', context.exception.error_code)

  def test_two_lines_start_with_spaces(self):
    with self.assertRaises(hedy.InvalidSpaceException) as context:
      result = hedy.transpile(" print Hallo welkom bij Hedy!\n print Hallo welkom bij Hedy!", self.level)
    self.assertEqual('Invalid Space', context.exception.error_code)

  def test_transpile_empty(self):
    with self.assertRaises(Exception) as context:
      result = hedy.transpile("", self.level)

  def test_transpile_ask(self):
    result = hedy.transpile("ask wat is je lievelingskleur?", self.level)
    expected = "answer = input('wat is je lievelingskleur?')"
    self.assertEqual(expected, result.code)
    self.assertEqual(False, result.has_turtle)

  def test_transpile_print_multiple_lines(self):
    result = hedy.transpile("print Hallo welkom bij Hedy\nprint Mooi hoor", self.level)
    expected = "print('Hallo welkom bij Hedy')\nprint('Mooi hoor')"
    self.assertEqual(expected, result.code)
    self.assertEqual(False, result.has_turtle)

  def test_transpile_three_lines(self):
    input = textwrap.dedent("""\
    print Hallo
    ask Wat is je lievelingskleur
    echo je lievelingskleur is""")

    expected = textwrap.dedent("""\
    print('Hallo')
    answer = input('Wat is je lievelingskleur')
    print('je lievelingskleur is'+answer)""")

    result = hedy.transpile(input, self.level)
    self.assertEqual(expected, result.code)
    self.assertEqual(False, result.has_turtle)

  def test_transpile_echo_without_argument(self):
    result = hedy.transpile("ask wat?\necho", self.level)
    expected = "answer = input('wat?')\nprint(answer)"
    self.assertEqual(expected, result.code)
    self.assertEqual(False, result.has_turtle)


  def test_use_quotes_in_print_allowed(self):
    code = "print 'Welcome to OceanView!'"
    result = hedy.transpile(code, self.level)

    expected = textwrap.dedent("""\
    print('\\'Welcome to OceanView!\\'')""")

    self.assertEqual(expected, result.code)
    self.assertEqual(False, result.has_turtle)

    expected_output = self.run_code(result)
    self.assertEqual("'Welcome to OceanView!'", expected_output)

  def test_use_slashes_in_print_allowed(self):
    code = "print 'Welcome to \O/ceanView!'"
    result = hedy.transpile(code, self.level)

    expected = textwrap.dedent("""\
    print('\\'Welcome to \\\\O/ceanView!\\'')""")

    self.assertEqual(expected, result.code)
    self.assertEqual(False, result.has_turtle)

    expected_output = self.run_code(result)
    self.assertEqual("'Welcome to \O/ceanView!'", expected_output)

  def test_use_slashes_at_end_of_print_allowed(self):
    code = "print Welcome to \\"
    result = hedy.transpile(code, self.level)

    expected = textwrap.dedent("""\
    print('Welcome to \\\\')""")

    self.assertEqual(expected, result.code)
    self.assertEqual(False, result.has_turtle)

    expected_output = self.run_code(result)
    self.assertEqual("Welcome to \\", expected_output)

  def test_use_quotes_in_ask_allowed(self):
    code = "ask 'Welcome to OceanView?'"
    result = hedy.transpile(code, self.level)

    expected = textwrap.dedent("""\
    answer = input('\\'Welcome to OceanView?\\'')""")

    self.assertEqual(expected, result.code)
    self.assertEqual(False, result.has_turtle)

  def test_lonely_echo(self):
    code = "echo wat dan?"
    with self.assertRaises(hedy.LonelyEchoException) as context:
      result = hedy.transpile(code, self.level)
    self.assertEqual('Lonely Echo', context.exception.error_code)

  def test_early_echo(self):
    code = textwrap.dedent("""\
    echo what can't we do?
    ask time travel """)
    with self.assertRaises(hedy.LonelyEchoException) as context:
      result = hedy.transpile(code, self.level)
    self.assertEqual('Lonely Echo', context.exception.error_code)

  def test_use_quotes_in_echo_allowed(self):
    code = textwrap.dedent("""\
    ask waar?
    echo oma's aan de """)

    result = hedy.transpile(code, self.level)

    expected = textwrap.dedent("""\
    answer = input('waar?')
    print('oma\\'s aan de '+answer)""")

    self.assertEqual(expected, result.code)
    self.assertEqual(False, result.has_turtle)

  def test_two_spaces_after_print(self):
    code = "print        hallo!"

    result = hedy.transpile(code, self.level)

    expected = textwrap.dedent("""\
    print('hallo!')""")

    self.assertEqual(expected, result.code)
    self.assertEqual(False, result.has_turtle)

  def test_newlines_only(self):
    code = textwrap.dedent("""\

    """)
    with self.assertRaises(hedy.EmptyProgramException) as context:
      result = hedy.transpile(code, self.level)
    self.assertEqual('Empty Program', context.exception.error_code)