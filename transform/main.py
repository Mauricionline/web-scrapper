import argparse
from urllib.parse import urlparse
import pandas as pd
import logging
import hashlib
import nltk
from nltk.corpus import stopwords

stopwords = set(stopwords.words('spanish'))

pd.options.display.max_rows = 30
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main(filename: str):
    logger.info('Starting cleaning process')

    df = _read_data(filename)
    newspaper_uid = _extract_newspaper_uid(filename)
    df = _add_newspaper_uid_column(df, newspaper_uid)
    df = _extract_host(df)
    df = _fill_missing_titles(df)
    df = _generate_uids_for_rows(df)
    df = _remove_new_extra_lines_from_title(df)
    df = _remove_new_extra_lines_from_body(df)
    df = _remove_new_extra_lines_from_category(df)
    df = _tokenize_column(df, 'title', 'n_tokens_title')
    df = _tokenize_column(df, 'body', 'n_tokens_body')
    df = _remove_duplicates_entries(df, 'title')
    df = _drop_rows_with_missing_values(df)
    _save_data(df, filename)
    return df


def _remove_new_extra_lines_from_category(df):
    logger.info('remove extra lines from category')
    stripped_category = (df
                         .apply(lambda row: row['category'], axis=1)
                         .apply(lambda body: list(str(body)))
                         .apply(lambda letters: list(map(lambda letter: letter.replace('\n', ''), letters)))
                         .apply(lambda letters: list(map(lambda letter: letter.replace('\t', ''), letters)))
                         .apply(lambda letters: list(map(lambda letter: letter.replace('\r', ''), letters)))
                         .apply(lambda letter: ''.join(letter))
                         )
    df['category'] = stripped_category
    return df


def _extract_host(df):
    logger.info('Extracting host from urls')
    df['host'] = df['url'].apply(lambda url: urlparse(url).netloc)
    return df


def _add_newspaper_uid_column(df, newspaper_uid):
    logger.info(f'Filling newspaper_uid columns with {newspaper_uid}')
    df['newspaper_uid'] = newspaper_uid
    return df


def _extract_newspaper_uid(filename):
    logger.info('Extranting newspaper uid')
    newspaper_uid = filename.split('_')[0]

    logger.info(f'Newspaper uid detected: {newspaper_uid}')
    return newspaper_uid


def _read_data(filename):
    logger.info(f'Reading file{filename}')
    return pd.read_csv(filename)


def _fill_missing_titles(df):
    logger.info('Filling missing titles')
    missing_titles_mask = df['title'].isna()

    missing_titles = (df[missing_titles_mask]['url']
                      .str.extract(r'(?P<missing_titles>[^/]+)$')
                      .applymap(lambda title: title.split('-'))
                      .applymap(lambda title_word_list: ' '.join(title_word_list))
                      )
    df.loc[missing_titles_mask, 'title'] = missing_titles.loc[:, 'missing_titles']
    return df


def _generate_uids_for_rows(df):
    logger.info('Generating uids for each row')
    uids = (df
            .apply(lambda row: hashlib.md5(bytes(row['url'].encode())), axis=1)
            .apply(lambda hash_object: hash_object.hexdigest())
            )
    df['uid'] = uids

    return df.set_index('uid')


def _remove_new_extra_lines_from_title(df):
    logger.info('remove extra lines from title')
    stripped_body = (df
                     .apply(lambda row: row['title'], axis=1)
                     .apply(lambda letters: letters.strip())
                     .apply(lambda title: list(str(title)))
                     .apply(lambda letters: list(map(lambda letter: letter.replace('\n', ''), letters)))
                     .apply(lambda letters: list(map(lambda letter: letter.replace('\t', ''), letters)))
                     .apply(lambda letters: list(map(lambda letter: letter.replace('\r', ''), letters)))
                     .apply(lambda letter: ''.join(letter))
                     )
    df['title'] = stripped_body
    return df


def _remove_new_extra_lines_from_body(df):
    logger.info('remove extra lines from body')
    stripped_body = (df
                     .apply(lambda row: row['body'], axis=1)
                     .apply(lambda body: list(str(body)))
                     .apply(lambda letters: list(map(lambda letter: letter.replace('\n', ''), letters)))
                     .apply(lambda letters: list(map(lambda letter: letter.replace('\t', ''), letters)))
                     .apply(lambda letters: list(map(lambda letter: letter.replace('\r', ''), letters)))
                     .apply(lambda letter: ''.join(letter))
                     )
    df['body'] = stripped_body
    return df


def _tokenize_column(df, column_name, new_column_name):
    logger.info(f'add tokenize column {new_column_name}')
    new_column = (df
                  .dropna()
                  .apply(lambda row: nltk.word_tokenize(row[column_name]), axis=1)
                  .apply(lambda tokens: list(filter(lambda token: token.isalpha(), tokens)))
                  .apply(lambda tokens: list(map(lambda token: token.lower(), tokens)))
                  .apply(lambda word_list: list(filter(lambda word: word not in stopwords, word_list)))
                  .apply(lambda valid_word_list: len(valid_word_list))
                  )
    df[new_column_name] = new_column
    return df


def _remove_duplicates_entries(df, column_name):
    logger.info('Removing duplicate entries')
    df.drop_duplicates(subset=[column_name], keep='first', inplace=True)
    return df


def _drop_rows_with_missing_values(df):
    logger.info('Dropping rows with missing values')
    return df.dropna()


def _save_data(df, filename):
    clean_file_name = f'clean_{filename}'
    logger.info(f'Saving data at location {clean_file_name}')
    df.to_csv(clean_file_name)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('filename', help='The path to the dirty data', type=str)

    arg = parser.parse_args()

    data_frame = main(arg.filename)
    print(data_frame)
