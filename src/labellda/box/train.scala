// Stanford TMT Example 6 - Training a LabeledLDA model
// http://nlp.stanford.edu/software/tmt/0.4/

// tells Scala where to find the TMT classes
import scalanlp.io._;
import scalanlp.stage._;
import scalanlp.stage.text._;
import scalanlp.text.tokenize._;
import scalanlp.pipes.Pipes.global._;
import edu.stanford.nlp.tmt.stage._;
import edu.stanford.nlp.tmt.model.lda._;
import edu.stanford.nlp.tmt.model.llda._;

val source = CSVFile("datafile.csv") ~> IDColumn(1);

val tokenizer = {
  SimpleEnglishTokenizer() ~>            // tokenize on space and punctuation
  CaseFolder() ~>                        // lowercase everything
  WordsAndNumbersOnlyFilter() ~>         // ignore non-words and non-numbers
  MinimumLengthFilter(1)                 // take terms with >=3 characters
}

val text = {
  source ~>                              // read from the source file
  Column(3) ~>                           // select column containing text
  TokenizeWith(tokenizer) ~>             // tokenize with tokenizer above
  TermCounter() ~>                       // collect counts (needed below)
  TermMinimumDocumentCountFilter(1) ~>   // filter terms in <4 docs
  TermDynamicStopListFilter(0) ~>      // filter out 30 most common terms
  DocumentMinimumLengthFilter(1)         // take only docs with >=5 terms
}

// define fields from the dataset we are going to slice against
val labels = {
  source ~>                              // read from the source file
  Column(2) ~>                           // take column two, the year
  TokenizeWith(WhitespaceTokenizer()) ~> // turns label field into an array
  TermCounter() ~>                       // collect label counts
  TermMinimumDocumentCountFilter(0)     // filter labels in < 10 docs
}

val dataset = LabeledLDADataset(text, labels);

// define the model parameters
val modelParams = LabeledLDAModelParams(dataset=dataset);

// Name of the output model folder to generate
val modelPath = file("modelfolder");

// Trains the model, writing to the given output path
TrainCVB0LabeledLDA(modelParams, dataset, output = modelPath, maxIterations = 50);
// TrainGibbsLabeledLDA(modelParams, dataset, output = modelPath, maxIterations = 1500);
