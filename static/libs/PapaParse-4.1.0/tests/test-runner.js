var passCount = 0;
var failCount = 0;
var testCount = 0;

$(function()
{
	// First, wireup!
	$('.results').on('click', 'td.rvl', function()
	{
		var tr = $(this).closest('tr');
		if (tr.hasClass('collapsed'))
		{
			$('.revealer', tr).hide();
			$('.hidden', tr).show();
			$(this).html("-");
		}
		else
		{
			$('.revealer', tr).show();
			$('.hidden', tr).hide();
			$(this).html("+");
		}
		tr.toggleClass('collapsed expanded');
	});

	$('.expand-all').click(function()
	{
		var $testGroup = $(this).closest('.test-group');
		$('.collapsed .rvl', $testGroup).click();
	});

	$('.collapse-all').click(function()
	{
		var $testGroup = $(this).closest('.test-group');
		$('.expanded .rvl', $testGroup).click();
	});

	function asyncDone()
	{
		// Finally, show the overall status.
		if (failCount == 0)
			$('#status').addClass('status-pass').html("All <b>" + passCount + "</b> test" + (passCount == 1 ? "" : "s") + " passed");
		else
			$('#status').addClass('status-fail').html("<b>" + failCount + "</b> test" + (failCount == 1 ? "" : "s") + " failed; <b>" + passCount + "</b> passed");
	}

	// Next, run tests and render results!
	runCoreParserTests();
	runParseTests(asyncDone);
	runUnparseTests();
	runCustomTests(asyncDone);

});


// Executes all tests in CORE_PARSER_TESTS from test-cases.js
// and renders results in the table.
function runCoreParserTests()
{
	for (var i = 0; i < CORE_PARSER_TESTS.length; i++)
	{
		var test = CORE_PARSER_TESTS[i];
		var passed = runTest(test);
		if (passed)
			passCount++;
		else
			failCount++;
	}

	function runTest(test)
	{
		var actual = new Papa.Parser(test.config).parse(test.input);
		var results = compare(actual.data, actual.errors, test.expected);
		displayResults('#tests-for-core-parser', test, actual, results);
		return results.data.passed && results.errors.passed
	}
}


// Executes all tests in PARSE_TESTS from test-cases.js
// and renders results in the table.
function runParseTests(asyncDone)
{
	for (var i = 0; i < PARSE_TESTS.length; i++)
	{
		var test = PARSE_TESTS[i];
		var passed = runTest(test);
		if (passed)
			passCount++;
		else
			failCount++;
	}

	var asyncRemaining = 0;

	PARSE_ASYNC_TESTS.forEach(function(test)
	{
		if (test.disabled)
			return;
		asyncRemaining++;
		var config = test.config;
		config.complete = function(actual)
		{
			var results = compare(actual.data, actual.errors, test.expected);

			displayResults("#tests-for-parse", test, actual, results);

			if (results.data.passed && results.errors.passed) {
				passCount++;
			} else {
				failCount++;
			}
			if (--asyncRemaining === 0) {
				asyncDone();
			}
		};

		config.error = function(err)
		{
			failCount++;
			displayResults("#tests-for-parse", test, {data:[],errors:err}, test.expected);
			if (--asyncRemaining === 0) {
				asyncDone();
			}
		};

		Papa.parse(test.input, config);
	});


	function runTest(test)
	{
		var actual = Papa.parse(test.input, test.config);
		var results = compare(actual.data, actual.errors, test.expected);
		displayResults('#tests-for-parse', test, actual, results);
		return results.data.passed && results.errors.passed
	}
}





function displayResults(tableId, test, actual, results)
{
	var testId = testCount++;

	var testDescription = (test.description || "");
	if (testDescription.length > 0)
		testDescription += '<br>';
	if (test.notes)
		testDescription += '<span class="notes">' + test.notes + '</span>';

	var tr = '<tr class="collapsed" id="test-'+testId+'">'
			+ '<td class="rvl">+</td>'
			+ '<td>' + testDescription + '</td>'
			+ passOrFailTd(results.data)
			+ passOrFailTd(results.errors)
			+ '<td class="revealable pre"><div class="revealer">condensed</div><div class="hidden">' + JSON.stringify(test.config, null, 2) + '</div></td>'
			+ '<td class="revealable pre"><div class="revealer">condensed</div><div class="hidden">' + revealChars(test.input) + '</div></td>'
			+ '<td class="revealable pre"><div class="revealer">condensed</div><div class="hidden">data: ' + JSON.stringify(test.expected.data, null, 4) + '\r\nerrors: ' + JSON.stringify(test.expected.errors, null, 4) + '</div></td>'
			+ '<td class="revealable pre"><div class="revealer">condensed</div><div class="hidden">data: ' + JSON.stringify(actual.data, null, 4) + '\r\nerrors: ' + JSON.stringify(actual.errors, null, 4) + '</div></td>'
		   + '</tr>';

	$(tableId+' .results').append(tr);

	if (!results.data.passed || !results.errors.passed)
		$('#test-'+testId+' td.rvl').click();

}


function compare(actualData, actualErrors, expected)
{
	var data = compareData(actualData, expected.data);
	var errors = compareErrors(actualErrors, expected.errors);

	return {
		data: data,
		errors: errors
	}


	function compareData(actual, expected)
	{
		var passed = true;

		if (actual.length != expected.length)
			passed = false;
		else
		{
			// The order is important, so we go through manually before using stringify to check everything else
			for (var row = 0; row < expected.length; row++)
			{
				if (actual[row].length != expected[row].length)
				{
					passed = false;
					break;
				}

				for (var col = 0; col < expected[row].length; col++)
				{
					var expectedVal = expected[row][col];
					var actualVal = actual[row][col];

					if (actualVal !== expectedVal)
					{
						passed = false;
						break;
					}
				}
			}
		}

		if (passed)	// final check will catch any other differences
			passed = JSON.stringify(actual) == JSON.stringify(expected);

		// We pass back an object right now, even though it only contains
		// one value, because we might add details to the test results later
		// (same with compareErrors below)
		return {
			passed: passed
		};
	}


	function compareErrors(actual, expected)
	{
		var passed = JSON.stringify(actual) == JSON.stringify(expected);

		return {
			passed: passed
		};
	}
}





// Executes all tests in UNPARSE_TESTS from test-cases.js
// and renders results in the table.
function runUnparseTests()
{
	for (var i = 0; i < UNPARSE_TESTS.length; i++)
	{
		var test = UNPARSE_TESTS[i];
		var passed = runTest(test);
		if (passed)
			passCount++;
		else
			failCount++;
	}

	function runTest(test)
	{
		var actual;

		try
		{
			actual = Papa.unparse(test.input, test.config);
		}
		catch (e)
		{
			if (e instanceof Error) {
				throw e;
			}
			actual = e;
		}

		var testId = testCount++;
		var results = compare(actual, test.expected);

		var testDescription = (test.description || "");
		if (testDescription.length > 0)
			testDescription += '<br>';
		if (test.notes)
			testDescription += '<span class="notes">' + test.notes + '</span>';

		var tr = '<tr class="collapsed" id="test-'+testId+'">'
				+ '<td class="rvl">+</td>'
				+ '<td>' + testDescription + '</td>'
				+ passOrFailTd(results)
				+ '<td class="revealable pre"><div class="revealer">condensed</div><div class="hidden">' + JSON.stringify(test.config, null, 2) + '</div></td>'
				+ '<td class="revealable pre"><div class="revealer">condensed</div><div class="hidden">' + JSON.stringify(test.input, null, 4) + '</div></td>'
				+ '<td class="revealable pre"><div class="revealer">condensed</div><div class="hidden">' + revealChars(test.expected) + '</div></td>'
				+ '<td class="revealable pre"><div class="revealer">condensed</div><div class="hidden">' + revealChars(actual) + '</div></td>'
			   + '</tr>';

		$('#tests-for-unparse .results').append(tr);

		if (!results.passed)
			$('#test-' + testId + ' td.rvl').click();

		return results.passed;
	}


	function compare(actual, expected)
	{
		return {
			passed: actual === expected
		};
	}
}




// Executes all tests in CUSTOM_TESTS from test-cases.js
// and renders results in the table.
function runCustomTests(asyncDone)
{
	var asyncRemaining = 0;
	for (var i = 0; i < CUSTOM_TESTS.length; i++)
	{
		runTest(CUSTOM_TESTS[i]);
	}

	function runTest(test)
	{
		if (test.disabled)
			return;
		asyncRemaining++;
		try
		{
			displayAsyncTest(test);
		}
		catch (e)
		{
			displayResults(test, e);
		}
	}

	function displayAsyncTest(test)
	{
		var testId = testCount++;
		test.testId = testId;

		var testDescription = (test.description || "");
		if (testDescription.length > 0)
			testDescription += '<br>';
		if (test.notes)
			testDescription += '<span class="notes">' + test.notes + '</span>';

		var tr = '<tr class="collapsed" id="test-'+testId+'">'
				+ '<td class="rvl">+</td>'
				+ '<td>' + testDescription + '</td>'
				+ '<td class="status pending">pending</td>'
				+ '<td class="revealable pre"><div class="revealer">condensed</div><div class="hidden">' + test.expected + '</div></td>'
				+ '<td class="revealable pre"><div class="revealer">condensed</div><div class="hidden actual"></div></td>'
				+ '</tr>';

		$('#custom-tests .results').append(tr);

		test.run(function(actual)
		{
			displayAsyncResults(test, actual);
		});

		setTimeout(function()
		{
			if (test.complete) return;
			displayAsyncResults(test, '(incomplete)');
		}, 2000);
	}

	function displayAsyncResults(test, actual)
	{
		var testId = test.testId;
		if (test.complete)
		{
			asyncRemaining++;
			actual = '(multiple results from test)';
		}
		test.complete = true;
		var results = compare(actual, test.expected);

		var tr = $('#test-'+testId);
		tr.find('.actual').text(actual);

		var status = $(passOrFailTd(results));
		var oldStatus = tr.find('.status');
		oldStatus.attr('class', status.attr('class'));
		oldStatus.text(status.text());

		if (!results.passed)
			$('#test-' + testId + ' td.rvl').click();

		if (results.passed)
			passCount++;
		else
			failCount++;

		if (--asyncRemaining === 0)
			asyncDone();
	}


	function compare(actual, expected)
	{
		return {
			passed: JSON.stringify(actual) === JSON.stringify(expected)
		};
	}
}








// Makes a TD tag with OK or FAIL depending on test result
function passOrFailTd(result)
{
	if (result.passed)
		return '<td class="status ok">OK</td>';
	else
		return '<td class="status fail">FAIL</td>';
}


// Reveals some hidden, whitespace, or invisible characters
function revealChars(txt)
{
	if (typeof txt != 'string')
		return '(file)';

	// Make spaces and tabs more obvious when glancing
	txt = txt.replace(/( |\t)/ig, '<span class="whitespace-char">$1</span>');
	txt = txt.replace(/(\r\n|\n\r|\r|\n)/ig, '<span class="whitespace-char special-char">$1</span>$1');

	// Make UNIT_SEP and RECORD_SEP characters visible
	txt = txt.replace(/(\u001e|\u001f)/ig, '<span class="special-char">$1</span>$1');

	// Now make the whitespace and invisible characters
	// within the spans actually appear on the page
	txt = txt.replace(/">\r\n<\/span>/ig, '">\\r\\n</span>');
	txt = txt.replace(/">\n\r<\/span>/ig, '">\\n\\r</span>');
	txt = txt.replace(/">\r<\/span>/ig, '">\\r</span>');
	txt = txt.replace(/">\n<\/span>/ig, '">\\n</span>');
	txt = txt.replace(/">\u001e<\/span>/ig, '">\\u001e</span>');
	txt = txt.replace(/">\u001f<\/span>/ig, '">\\u001f</span>');

	return txt;
}
