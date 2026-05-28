import json

data = json.load(open('multi_city_results/multi_city_training_results.json'))
print('Available transfers:')
for t in data['transfer_results']:
    print(f"  {t['source'][:3]} -> {t['target'][:3]}: {t['zero_shot_acc']:.2f}%")
