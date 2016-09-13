package eu.nomad_lab.parsers

import org.specs2.mutable.Specification

object FleurTests extends Specification {
  "FleurParserTest" >> {
    "test with json-events" >> {
      ParserRun.parse(FleurParser, "parsers/fleur/test/examples/ok/out", "json-events") must_== ParseResult.ParseSuccess
    }
    "test with json" >> {
      ParserRun.parse(FleurParser, "parsers/fleur/test/examples/ok/out", "json") must_== ParseResult.ParseSuccess
    }
  }
}
