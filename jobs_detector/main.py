from __future__ import print_function
import click
import requests
from bs4 import BeautifulSoup
from .settings import BASE_URL, BASE_DIR
from .exceptions import InvalidURLException


DEFAULT_KEYWORDS = ['Remote', 
                    'Postgres', 
                    'Python', 
                    'Javascript',
                    'React',
                    'Pandas']

@click.group()
def jobs_detector():
    pass

@jobs_detector.command()
@click.option('-i', '--post-id', type=str, required=True, help='[required]')
@click.option('-k', '--keywords', type=str, default=','.join(DEFAULT_KEYWORDS))
@click.option('-c', '--combinations', type=str,
              callback=lambda _, x: x.split(',') if x else x)

def hacker_news(post_id, keywords, combinations=None):
    keywords = [word for word in keywords.split(',')]

    r = requests.get(BASE_URL.format(post_id))
    if r.status_code != 200:
        raise InvalidURLException
    
    soup = BeautifulSoup(r.text, 'html.parser')
    
    comment_tree = soup.find_all("tr", ["athing", "athing comtr "]) 
    job_posts = []
    for comment in comment_tree:
        if comment.select('img'):
            comment_width = int(comment.select('img')[0].get('width'))
            if comment_width == 0:
                job_posts.append(comment)

    #Parse "who is hiring?" HackerNews posts based on given set of keywords.
    
    count_dict = {key:0 for key in keywords}
    job_posts_found = 0
    for comment in job_posts:
        for word in keywords:
            if word.lower() in comment.text.lower():
                count_dict[word] += 1
                job_posts_found += 1
   
    if combinations:
        combination_check_list = [item.split('-') for item in combinations]
        combination_dict = {key:0 for key in combinations}

        for comment in job_posts:
            for index, combo in enumerate(combination_check_list):
                if [word for word in combo if word.lower() in comment.text.lower()] == combo:
                    combination_dict[combinations[index]] += 1
                else:
                    break
        
    
    expected_list = ['Total job posts: {0}'.format(len(job_posts)), 'Keywords:']

    for key, val in count_dict.items():
        expected_list.append('{0}: {1} ({2}%)'.format(key, val, int(val/float(len(job_posts))*100)))
    
    if combinations:
        expected_list.append('Combinations:')
        for key, val in combination_dict.items():
            expected_list.append('{0}: {1} ({2}%)'.format(key, val, int(val/float(len(job_posts))*100)))
    
    print(expected_list)


if __name__ == '__main__':
    jobs_detector()
